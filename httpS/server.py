#!/usr/bin/env python
# -*- coding:utf-8 -*-

# httpS 服务器一般流程

import socket
import datetime
import re

class HttpRequest(object):

    def __init__(self,client_socket,client_address):
        self.__querys={}
        request_data = client_socket.recv(2048)
        # 将接受到的字节流数据转换成字符串类型
        request_data = request_data.decode()
        # 将接受到的数据分为 请求头部数据 和 请求体数据
        request_head_data,request_body_data = request_data.split('\r\n\r\n')
        # 将请求头部的数据分割，获取每一部分
        request_head_datas = request_head_data.split('\r\n')
        # 获得请求行数据
        request_line_data = request_head_datas[0]
        print(request_line_data)
        # 获得请求头数据
        request__heads = request_head_datas[1:]
        # 封装请求行
        self.wrap_request_line(request_line_data)
        # 封装请求体
        self.wrap_request_body(request_body_data)
        # 封装请求头,封装成字典k,v格式
        self.wrap_headers(request__heads,client_address)
        print(self.headers)   #打印一下封装后的请求头
        # 打印一下封装后的来访者IP，来访时间
        print('来访者 ip:%s , 时间:%s , 请求方式:%s , 请求路径:%s '%(self.headers.get('remote'),str(datetime.datetime.today()),self.METHOD,self.PATH))
        # print('host:'+self.headers.get('Host'))   #想得到的数据通过字典的方式得到
        print(self.get_query('name'))
        # 打印POST请求体
        print('POST请求体:%s'%request_body_data)
    # 封装请求头
    def wrap_headers(self, request_heads,client_address):
        self.headers = {}
        for head in request_heads:
            # 用:进行切割时，注意 host : 127.0.0.1:8000 这条记录容易导致切割失败
            index = head.find(':')
            k,v= head[0:index],head[index+1:]      #解决办法
            # self.headers[('http_'+k).upper()]=v  #django处理请求头封装的写法
            self.headers[k]=v
        self.headers['remote']=str(client_address)
    # 封装请求行
    def wrap_request_line(self, request_line_data):
        #得到请求行中的 请求方式 请求路径(用来做路由使用) 请求协议
        self.METHOD,self.PATH,self.SCHEMA = request_line_data.split()
        if self.METHOD.lower() == 'get' and self.PATH.find('?')!=-1:
            print('封装了get参数')
            #self.PATH(请求路径) querys(请求参数)
            self.PATH,querys = self.PATH.split('?')
            #封装请求参数
            self.wrap_querys(querys)
    #分装请求参数
    def wrap_querys(self, querys):
        for query in querys.split('&'):
            k,v = query.split('=')
            self.__querys[k]=v
    # 通过k得到请求方式——没有写set方法用来设置请求参数（因为请求参数都是只读的）
    def get_query(self,k,default=None):
        return self.__querys.get(k,default)
    # 封装请求体，以及请求体中的参数
    def wrap_request_body(self, request_body_data):
        if self.METHOD.lower() == 'post':
           self.wrap_querys(request_body_data)


class HttpServer(object):

    __is_start=True

    def __init__(self,address=('',8000),backlog=5,routers=None):
        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.server_socket.bind(address)
        self.server_socket.listen(backlog)

    def start(self):
        while self.__is_start:
            client_socket,client_address = self.server_socket.accept()
            httprequest = HttpRequest(client_socket,client_address)
            self.__dispatch(httprequest,client_socket)
    def stop(self):
        self.__is_start=False
        self.server_socket.close()

    def __dispatch(self, httprequest,client_socket):
        handler = None
        for path,handler_clz in routers:
            if re.match(path,httprequest.PATH) :
                handler = handler_clz
                break
        if handler != None:
            handler=handler()
            # handler.request = httprequest   老方法
            handler.set_request(httprequest)
            # 9种http请求方式，  GET / HTTP1.1 ABC / HTTP1.1   都可以用这个代码
            content = getattr(handler,httprequest.METHOD.lower())()
            content = content.encode()
            client_socket.send(b'HTTP/1.1 200 ok\r\n')
            client_socket.send(b'Server: diy server\r\n')
            client_socket.send(b'\r\n')
            client_socket.send(content)
            client_socket.close()


class  RequestHandler(object):
    __request = None
    # 设置httpRequest
    def set_request(self,request):
        self.__request =request
    # 得到参数
    def get_query(self,key,default):
      return self.__request.get_query(key,default)

# 两个不同的路由
class IndexRequest(RequestHandler):
    def get(self):
        return 'hello get'+self.get_query('name','meiyou')
    def post(self):
        return 'hello post'+self.get_query('name','meiyou')+self.get_query('age','meiyou')
    def abc(self):
        return 'hello abc'
class ShowRequest(RequestHandler):
    def get(self):
        return  'hello ShowRequesst'

# 路由，通过正则匹配
routers=[
    (r'^/$',IndexRequest),
    (r'^/show/$',ShowRequest),
]

server = HttpServer(address=('',9001),routers=routers)
server.start()