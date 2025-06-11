# Socks5Server
一个轻量级Socks5服务端，适用于个人用的小规模流量转发代理，使得内网中的前端机器变得能够访问互联网中的服务器。  

## 1. 下载文件

选择一个能连接互联网的服务器，在服务器上使用 `curl` 下载本项目：

```bash
curl -O https://raw.githubusercontent.com/Natsumejuri/Socks5Server/main/socks5.py
```
## 2. 启动服务端

确保你已经安装了 Python 3（推荐 Python 3.6 及以上）。

然后在项目目录下运行：

```bash
python socks5.py
```
在第一次运行中，若没有配置文件，程序会在你的工作目录下生成一个配置文件`config.json`并退出，`config.json`中包含了  
`PORT`:监听端口  
`MAX_CONNECTIONS`:最大连接数  
`USERS`:用户名和密码  

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

本程序支持多用户，每个字典组以`,`半角逗号隔开以添加新用户  
```json
{
    "PORT": 1080,
    "MAX_CONNECTIONS": 100,
    "USERS": [
        {"username": "user1", "password": "pass1"},
        {"username": "user2", "password": "pass2"}
    ]
}

```

最后，服务端启动成功时，你可以拿任何支持Socks5协议的客户端使用Socks5服务器代理流量。
