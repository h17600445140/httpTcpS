#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ——————————多进程版TCP服务器模板——————————

import socket
from multiprocessing import Process   #进程
from threading import Thread          #线程

# django,tornado 都是tcp，java也是

def handle_request(client_socket):
    client_request_date = client_socket.recv(2048)   # 从客服端接收的请求数据
    print(client_request_date)
    client_socket.send(b'HTTP/1.1 200 ok\r\n')       # 响应行
    client_socket.send(b'Name: huangchao\r\n')       # 响应头 1：主机名：姓名 ：给谁：helowolrd
    client_socket.send(b'\r\n')                      # 响应空行
    client_socket.send(b'hello huangchao')           # 响应体
    # client_socket.close()

def main():
    # AF_INET 互联网协议   SOCK_STREAM tcp   SOCK_DGRAM udp
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 设置应用结束，端口立即释放
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 绑定端口
    server_socket.bind(('', 9090))
    # 监听，同时最多有多少个请求能够处理
    server_socket.listen(128)
    while True:
        # 接受到的是一个元组（分别是新的客服端套接字和一个客服端地址<ip+端口>）
        client_socket, client_address = server_socket.accept()
        handle_process = Process(target=handle_request, args=(client_socket,))
        handle_process.start()
        client_socket.close()

if __name__ == '__main__':
    main()