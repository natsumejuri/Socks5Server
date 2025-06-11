import socket
import threading
import struct
import json
import os
import sys

default_config={
    "PORT":1080,
    "MAX_CONNECTIONS":100,
    "USERS":[]
}

#第一次启动时初始化配置文件
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")

if not os.path.exists(config_path):
    with open(config_path,'w',encoding='utf-8') as f:
        json.dump(default_config,f,indent=4)
    print(f"[info] Configuration file '{config_path}' does not exist. A default configuration has been created. Please modify it and run again.")
    sys.exit(0)
#读取文件
try:
    with open(config_path,'r',encoding='utf-8') as f:
        config=json.load(f)
except json.JSONDecodeError as e:
    print(f"[error] Configuration file format error: {e}")
    sys.exit(1)

PORT=config.get("PORT")
MAX_CONNECTIONS=config.get("MAX_CONNECTIONS")
USER={u["username"]:u["password"] for u in config.get("USERS",[])}

def handle_client(client_socket):
    try:
        #协商阶段
        ver,nmethods=struct.unpack("!BB",client_socket.recv(2))
        if ver!=5:
            client_socket.sendall(b"\x05\xFF")
            client_socket.close()
            return
        methods=client_socket.recv(nmethods)

        if 0x00 in methods:
            client_socket.sendall(b"\x05\x00")
            
        elif 0x02 in methods:
            client_socket.sendall(b"\x05\x02")
            ver=client_socket.recv(1)[0]
            ulen=client_socket.recv(1)[0]
            uname=client_socket.recv(ulen).decode()
            plen=client_socket.recv(1)[0]
            passwd=client_socket.recv(plen).decode()

            if USER.get(uname)==passwd:
                client_socket.sendall(b"\x01\x00")
            else:
                client_socket.sendall(b"\x01\x01")
                client_socket.close()
                return
            
        else :
            client_socket.sendall(b"\x05\xFF")
            client_socket.close()
            return


        #请求阶段,仅接受CONNECT命令
        ver,cmd,rev,atyp=struct.unpack("!BBBB",client_socket.recv(4))

        if atyp==1:
            addr=socket.inet_ntoa(client_socket.recv(4))
        elif atyp==3:
            length=client_socket.recv(1)[0]
            addr=client_socket.recv(length).decode()
        elif atyp==4:
            ipv6=client_socket.recv(16)
            addr=socket.inet_ntop(socket.AF_INET6,ipv6)
        else:
           client_socket.close()
           return
        port=struct.unpack("!H",client_socket.recv(2))[0]
        
        if cmd==1:
            try:
               remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
               remote.connect((addr, port))
               bind_address = remote.getsockname()
               address = struct.unpack("!I", socket.inet_aton(bind_address[0]))[0]
               port = bind_address[1]
               reply = struct.pack("!BBBBIH", 5, 0, 0, 1, address, port)
               client_socket.sendall(reply)
            except Exception as e:
               reply=b"\x05\x01\x00\x01\x00\x00\x00\x00\x00\x00"
               client_socket.sendall(reply)
               client_socket.close()
               return
        else:
            reply=b"\x05\x07\x00\x01\x00\x00\x00\x00\x00\x00"
            client_socket.sendall(reply)
            client_socket.close()
            return
        
        
        forward_data(client_socket,remote)
        
    except Exception as e:
        print(f"[error] Exception as {e}")
    finally:
        client_socket.close()

#流量转发
def forward_data(sock1,sock2):
    def forward(src,dst):
         try:
            while True:
                data=src.recv(4096)
                if not data:
                    break
                dst.sendall(data)
         except Exception as e:
               print(f"[error] Exception occurred during forwarding: {e}")
    t1=threading.Thread(target=forward,args=(sock1,sock2))
    t2=threading.Thread(target=forward,args=(sock2,sock1))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    #统一关闭socket
    for s in (sock1, sock2):
        try:
            s.shutdown(socket.SHUT_RDWR)
        except:
            pass
        s.close()  

#主函数
def main():         
    host='0.0.0.0'
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((host,PORT))
    server.listen(MAX_CONNECTIONS)
    print(f"Listening on {host}:{PORT}")
    while True:
        client_socket=server.accept()[0]
        threading.Thread(target=handle_client,args=(client_socket,)).start()

if __name__ == "__main__":
    main()