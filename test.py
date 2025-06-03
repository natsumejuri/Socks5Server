import socks
import socket

# 设置socks5代理
IP,PORT = input ( "请以IP:端口号格式输入代理服务器地址:" ).split(":")
PORT=int(PORT)
socks.set_default_proxy(socks.SOCKS5, IP, PORT)
socket.socket = socks.socksocket

# 测试连接
try:

    import urllib.request
    print(urllib.request.urlopen('https://google.com').read())
except Exception as e:
    print(f"连接失败:{e}")

