# Socks5Server
Socks5服务端，用于代理转发流量，使得内部网中的前端机器变得能够访问Internet网中的服务器
## 1. 下载文件

使用 `curl` 下载本项目到本地：

```bash
curl -O https://raw.githubusercontent.com/Natsumejuri/Socks5Server/main/socks5.py
```
## 2. 启动服务端

确保你已经安装了 Python 3（推荐 Python 3.6 及以上）。

然后在项目目录下运行：

```bash
python socks5.py
```
在第一次运行中，程序会在你的工作目录下生成一个配置文件`config.json`，其中包含了  

```json
{
    "PORT": 1080,
    "MAX_CONNECTIONS": 100,
    "USERS": []
}
```
若想添加用户验证，请在USERS内添加字典，每个字典以`,`半角逗号隔开  
```json
{
    "PORT": 1080,
    "MAX_CONNECTIONS": 100,
    "USERS": [
        {"username": "user1", "password": "pass1"}
    ]
}

```
其中`user1`改为你想设定的用户名，`pass1`改为你想设定的密码  

最后，服务端启动成功时，若网络连接无误，你可以拿任何支持Socks5协议的客户端使用Socks5服务器代理流量。
