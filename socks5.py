import socket
import threading
import struct
def handle_client(client_socket):
    try:
        #协商阶段，仅接受0x00连接方式
        ver,nmethods=struct.unpack("!BB",client_socket.recv(2))
        assert ver==5
        methods=client_socket.recv(nmethods)

        if 0x00 not in methods:
            client_socket.sendall(b"\x05\xFF")
            client_socket.close()
            return
        client_socket.sendall(b"\x05\x00")
        #请求阶段,仅接受CONNECT命令
        ver,cmd,rev,atyp=struct.unpack("!BBBB",client_socket.recv(4))
        assert ver==5

        if atyp==1:
            addr=socket.inet_ntoa(client_socket.recv(4))
        elif atyp==3:
            length=client_socket.recv(1)[0]
            addr=client_socket.recv(length).decode()
        else:
           client_socket.close()
           return
        port=struct.unpack("!H",client_socket.recv(2))[0]
        
        if cmd==1:
            try:
               print(f"目标地址：{addr}:{port}")
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
        print(f"Exception as {e}")
    finally:
        client_socket.close()
def forward_data(sock1,sock2):
    def forward(src,dst):
         try:
            while True:
                data=src.recv(4096)
                if not data:
                    break
                dst.sendall(data)
         except:
            pass
         finally:
             src.close()
             dst.close()
    t1=threading.Thread(target=forward,args=(sock1,sock2))
    t2=threading.Thread(target=forward,args=(sock2,sock1))
    t1.start()
    t2.start()
            
host='0.0.0.0'
port=1080
server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((host,port))
server.listen(100)
print(f"正在监听{host}:{port}")
while True:
    client_socket,addr=server.accept()
    threading.Thread(target=handle_client,args=(client_socket,)).start()