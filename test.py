import asyncio
import socket
import struct
import time

#本测试脚本由Chatgpt师傅编写

SOCKS5_HOST = '127.0.0.1'
SOCKS5_PORT = 1080
USERNAME = None  # 如有需要可填 "your_username"
PASSWORD = None  # 如有需要可填 "your_password"
CONCURRENCY = 100  # 并发连接数
TARGET_ADDR = '172.217.31.142'#google.com
TARGET_PORT = 80

async def test_socks5_connection(index):
    reader, writer = await asyncio.open_connection(SOCKS5_HOST, SOCKS5_PORT)

    try:
        # 发起协商
        if USERNAME and PASSWORD:
            writer.write(b'\x05\x01\x02')  # VER, NMETHODS=1, USERNAME/PASSWD
            await writer.drain()

            # 认证阶段
            resp = await reader.readexactly(2)
            if resp != b'\x05\x02':
                print(f"[{index}] Auth method not accepted")
                return False

            uname = USERNAME.encode()
            passwd = PASSWORD.encode()
            writer.write(b'\x01' + bytes([len(uname)]) + uname + bytes([len(passwd)]) + passwd)
            await writer.drain()

            auth_status = await reader.readexactly(2)
            if auth_status[1] != 0x00:
                print(f"[{index}] Auth failed")
                return False
        else:
            writer.write(b'\x05\x01\x00')  # VER, NMETHODS=1, NO AUTH
            await writer.drain()
            resp = await reader.readexactly(2)
            if resp[1] != 0x00:
                print(f"[{index}] Server refused no-auth")
                return False

        # 发送 CONNECT 请求
        writer.write(
            b'\x05\x01\x00\x01' + socket.inet_aton(TARGET_ADDR) + struct.pack("!H", TARGET_PORT)
        )
        await writer.drain()

        resp = await reader.readexactly(10)
        if resp[1] == 0x00:
            print(f"[{index}] CONNECT success")
            return True
        else:
            print(f"[{index}] CONNECT failed: {resp[1]}")
            return False

    except Exception as e:
        print(f"[{index}] Error: {e}")
        return False
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    print(f"[info] Starting {CONCURRENCY} concurrent connections...")
    start_time = time.time()

    tasks = [test_socks5_connection(i) for i in range(CONCURRENCY)]
    results = await asyncio.gather(*tasks)

    success = sum(results)
    print(f"[info] {success}/{CONCURRENCY} connections succeeded.")
    print(f"[info] Elapsed: {time.time() - start_time:.2f} seconds")

if __name__ == '__main__':
    asyncio.run(main())
