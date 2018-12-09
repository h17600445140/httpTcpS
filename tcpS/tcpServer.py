#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 传统的TCP服务器模板，步骤如下
# （只处理一次）

import socket

# AF_INET 互联网协议   SOCK_STREAM tcp   SOCK_DGRAM udp
# 1、
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 设置应用结束，端口立即释放
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# 绑定端口
# 2、
server_socket.bind(('', 8080))
# 监听，同时最多有多少个请求能够处理
# 3、
server_socket.listen(128)
# 接受到的是一个元组（分别是新的客服端套接字和一个客服端地址<ip+端口>）
# 4、
client_socket, client_address = server_socket.accept()
# 从客服端接受到的数据
client_request_date = client_socket.recv(2048)
print(client_request_date)   #请求的数据，包括请求行、请求头、请求空行、请求体
# 给客服端发数据，注意：需要将发送的字符串转换为字节流，字节流在网络上传输
# bytes变为str，就需要用decode()方法，反之亦然
# 5、
# ——————这三行的目的是让浏览器接收到消息————————
client_socket.send('HTTP/1.1 200 ok\r\n'.encode())  # 响应行
client_socket.send('Name: zhangsan\r\n'.encode())   # 响应头 1：主机名：姓名 ：给谁：helowolrd
client_socket.send('\r\n'.encode())                 # 响应空行
# ——————————————————————————————
client_socket.send('hello python'.encode())         # 响应体
# 关闭 服务端，客服端 的 socket 连接
server_socket.close()
client_socket.close()

