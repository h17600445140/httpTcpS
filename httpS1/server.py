#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 面向对象的角度封装了三个类 请求 响应 服务

import datetime
import socket
import uuid
import re
import os

# 根目录路径 os.path.dirname 指当前目录的父目录
TEMPATE_PATH=os.path.dirname(os.path.dirname(__file__))
BASE_DIR = TEMPATE_PATH

# ——————————Session——————————
class Session(object):
    def __init__(self):
        self.__sessionid = ''.join(str(uuid.uuid4()).split('-'))
        self.__cache = {}
    def set(self,k,v):
        self.__cache[k]=v
    def get(self,k,defualut=None):
        return self.__cache.get(k,defualut)
    def clear(self):
        self.__cache.clear()
    def get_sessionid(self):
        return self.__sessionid

# 单例模式，确保某一个类只有一个实例
class SessionManager(object):
    __caches={}
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'instance'):
            setattr(cls,'instance',super(SessionManager,cls).__new__(cls))
        return getattr(cls,'instance')
    # 通过sessionid得到内存中存储的session
    def get_session(self,sessionid):
        if sessionid == None :
            sessionid=""
        session = self.__caches.get(sessionid,None)
        if session == None :
            session = Session()
            self.__caches[session.get_sessionid()]=session
        return session
# ——————————Session——————————

# ————————————————————————
class HttpRequest(object):

    def __init__(self,client_socket,client_address):
        self.__querys={}
        self.__cookies = {}
        request_data = client_socket.recv(2048)
        # 将接受到的字节流数据转换成字符串类型
        request_data = request_data.decode()
        # 将接受到的数据分为 请求头部数据 和 请求体数据
        request_head_data,request_body_data = request_data.split('\r\n\r\n')
        # 将请求头部的数据分割，获取每一部分
        request_head_datas = request_head_data.split('\r\n')
        # 获得请求行数据
        request_line_data = request_head_datas[0]
        # print(request_line_data)
        # 获得请求头数据
        request__heads = request_head_datas[1:]
        # 封装请求行
        self.wrap_request_line(request_line_data)
        # 封装请求体
        self.wrap_request_body(request_body_data)
        # 封装请求头,封装成字典k,v格式
        self.wrap_headers(request__heads,client_address)
        # 封装cookies
        self.wrap_cookies()
        # 封装sessions
        self.wrap_session()
        # print(self.headers)   #打印一下封装后的请求头
        # 打印一下封装后的来访者IP，来访时间
        print('来访者 ip:%s , 时间:%s , 请求方式:%s , 请求路径:%s '%(self.headers.get('remote'),str(datetime.datetime.today()),self.METHOD,self.PATH))
        # print('host:'+self.headers.get('Host'))   #想得到的数据通过字典的方式得到
        # print(self.get_query('name'))
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
    # 封装请求体，以及请求体中的参数
    def wrap_request_body(self, request_body_data):
        if self.METHOD.lower() == 'post':
           self.wrap_querys(request_body_data)
    # 封装请求参数
    def wrap_querys(self, querys):
        # 没有直接返回
        querys = querys.strip()
        if len(querys) == 0: return
        for query in querys.split('&'):
            k,v = query.split('=')
            self.__querys[k]=v
    # 通过k得到请求参数——没有写set方法用来设置请求参数（因为请求参数都是只读的）
    def get_query(self,k,default=None):
        return self.__querys.get(k,default)

    # 封装cookies，得到cookie的两种方法
    def wrap_cookies(self):
        cookies = self.headers.get('Cookie', None)
        if cookies != None:
            for cookie in cookies.split(';'):
                k,v = cookie.split('=')
                self.__cookies[k.strip()]=v
    def get_cookie(self,key,default=None):
        return self.__cookies.get(key,default)
    def get_cookie_items(self):
        return self.__cookies.items()

    # 封装sessions
    def wrap_session(self):
        sessionid = self.get_cookie('sessionid')
        # 去存储查找
        # 通过sessionid得到服务器中存储的session对象
        session = SessionManager().get_session(sessionid)
        self.session = session


class HttpResponse(object):
    def __init__(self,content):
        self.headers={}
        # 初始化响应头
        self.init_heads()
        # 传回去的内容，响应体
        self.content = content

    def __str__(self):
        # 响应行
        self.response_line = 'HTTP/1.1 200 ok\r\n'
        self.response_blank_line = '\r\n'
        # ——将响应行的内容封装在响应的数据中
        response_data =self.response_line
        # ——将响应头的内容封装在响应的数据中
        for k,v in self.headers.items():
            head = k+":"+v+"\r\n"
            response_data+=head
        # ——将响应空行的内容封装在响应的数据中
        response_data+=self.response_blank_line
        # ——将响应体的内容封装在响应的数据中
        response_data+=self.content
        # ——传回去的响应数据
        return response_data
    # 初始化自定义默认的响应头
    def init_heads(self):
        self.headers['Server']=' My Server'
        self.headers['Content-Type']=' text/html;charset=utf-8'
    # 响应头中设置cookies
    def set_cookie(self,name,value,path='/'):
        # Set-Cookie: BDSVRTM = 307; path = /   #响应头中设置cookies的基本格式
        key = 'Set-Cookie'
        value = ' %s=%s;path=%s'%(name,value,path)
        self.headers[key]=value


class HttpRedirctResponse(object):
    def __init__(self, redirect):
        # Location: https: // www - temp.example.org /
        self.headers = {}
        self.headers['Location']=" %s"%redirect
        self.init_heads()
        self.content = ""

    def __str__(self):
        # 重定向请求行
        self.response_line = 'HTTP/1.1 302 Found\r\n'
        self.response_blank_line = '\r\n'
        response_data = self.response_line
        for k, v in self.headers.items():
            head = k + ":" + v + "\r\n"
            response_data += head
        response_data += self.response_blank_line
        response_data += self.content
        return response_data

    def set_cookie(self, name, value, path='/'):
        # Set-Cookie: BDSVRTM = 307; path = /
        key = 'Set-Cookie'
        value = ' %s=%s;path=%s' % (name, value, path)
        self.headers[key] = value

    def init_heads(self):
        self.headers['Server'] = ' My Server'
        self.headers['Content-Type'] = ' text/html;charset=utf-8'


class HttpServer(object):

    __is_start = True

    def __init__(self,address=('',8000),backlog=5,routers=None,static_url='/static',static_file_dir='static'):
        self.routers = routers
        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.server_socket.bind(address)
        self.server_socket.listen(backlog)
        # ——————静态文件——————
        self.static_url = static_url
        self.static_file_dir = os.path.join(BASE_DIR,static_file_dir)

    def start(self):
        while self.__is_start:
            client_socket,client_address = self.server_socket.accept()
            httprequest = HttpRequest(client_socket,client_address)
            # init初始化全局上下文，在httprequest刚刚创建的时候初始化
            # httpRequest.data={}   初始化全局的字典，使所有的httpRequest都有全局的上下文字典
            self.__dispatch(httprequest,client_socket)

    def stop(self):
        self.__is_start=False
        self.server_socket.close()

    def __dispatch(self, httprequest,client_socket):
        # ——————处理静态文件——————
        if httprequest.PATH.startswith(self.static_url):
            # 映射 /static/index.html > static.file_dir/index.html
            path = httprequest.PATH[len(self.static_url)+1:]
            with open(os.path.join(self.static_file_dir,path)) as fr:
                content = fr.read()
            response = HttpResponse(content)
            response = str(response).encode()
            client_socket.send(response)
            client_socket.close()
            return
        # ——————————————————
        handler = None
        for path,handler_fun in self.routers:
            if re.match(path,httprequest.PATH) :
                handler = handler_fun
                break
        if handler != None:
            response = handler(httprequest)
            # ——————处理sessionid——————
            sessionid = httprequest.get_cookie('sessionid')
            if sessionid != httprequest.session.get_sessionid():
                response.set_cookie('sessionid', httprequest.session.get_sessionid())
            # ——————————————————
            # 传回去的响应数据必须转码
            response = str(response).encode()
            client_socket.send(response)
            client_socket.close()
# ————————————————————————

def render(template_name):
    with open(os.path.join(TEMPATE_PATH,template_name)) as fr:
        content = fr.read()
    # 未知问题
    return  HttpResponse(content.strip())