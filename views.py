#!/usr/bin/env python
# -*- coding:utf-8 -*-

import uuid
from httpS1.server import *

class User(object):
    def __init__(self,account,password):
        self.account = account
        self.password = password

# 框架如果没有中间件，就用装饰器来处理中间件
# ————————自定义装饰器中间件————————
class UserAuth(object):
    def __init__(self,get_response):
        self.get_response = get_response
    def __call__(self, request ,*args, **kwargs):
        if request.PATH.startswith('/user'):
            return HttpResponse('未经授权')
        # 真实处理
        return self.get_response(request)
class User2Auth(object):
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request, *args, **kwargs):
        if request.PATH.startswith('/user'):
            return HttpResponse('未经授权User2Auth')
        return self.get_response(request)
class User3Auth(object):
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request, *args, **kwargs):
        response = self.get_response(request)
        response.content = '<font color="red">%s</font>'%response.content
        return response
# —————————中间件———————————

def index_view(request):
    response = render('login.html')
    # 设置cookies的方法
    # response.set_cookie('sessionid',''.join(str(uuid.uuid4()).split('-')))
    return response

def login_view(request):
    account = request.get_query('account')
    password = request.get_query('password')
    if account == 'huangchao' and password == '123456789':
        # return HttpResponse('用户登录成功,欢迎'+account)
        request.session.set('user', User(account=account, password=password))
        return HttpRedirctResponse('http://127.0.0.1:9001/usercenter')
    else:
        return HttpRedirctResponse('http://127.0.0.1:9001')

@User3Auth  # 变为红字（中间件）
# @User2Auth  # 最终结果为 未经授权User2Auth
# @UserAuth  # 通过包装后 user = UserAuth(user) 对象 # user(request) = UserAuth(user)()
def user(request):
    # return HttpResponse('欢迎：***')
    return HttpResponse('欢迎:%s'%request.session.get('user','当前没有登录').password)

# 演示得到Cookies
def show(request):
    for k,v in request.get_cookie_items():
        print('cookie :',k,v)
    return HttpResponse('hello show')

# 演示模板渲染过程，简单的实现，原则是使用正则匹配标签（最终都要读到内存中对其进行操作）
def tem(reuqest):
    with open('XuanRan.html') as fr:
        content = fr.read()
    content = content.replace('{{name}}','HuangChao')
    return HttpResponse(content)

# 路由，通过正则匹配
routers=[
    (r'^/$',index_view),
    (r'^/show$',show),
    (r'^/login$',login_view),
    (r'^/usercenter$', user),
    (r'^/tem$', tem),
]

server = HttpServer(address=('',9001),routers=routers,static_url='/hc',static_file_dir='staticfile')
server.start()