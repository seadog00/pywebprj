#-*- coding:utf-8 -*-
__author__ = 'Alpher'

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseServerError
from profiles.forms import *
import os
from mysite import settings
from PIL import Image
import base64
# from django.http import Http404
#from django.http import HttpResponse

# Create your views here.

# @login_required
def homeindex(request):
	"""首页"""
	#用户已登陆
	if request.user.is_authenticated():
		showname = getName(request)
		anymous = False
	else:
		showname = u'游客'
		anymous = True
	return render(request,'index.html',{'showname':showname,'hostinfo':request.get_host(),'isStaff':request.user.is_staff,'anymous':anymous})

@login_required
def saveUserInfo(request):
	"""账号管理页"""
	SEX={u'男':'1',u'女':'2'}

	cur_user=User.objects.get(username=request.user.username)
	userid=cur_user.id
	username=cur_user.username
	userdj=cur_user.date_joined.strftime("%Y-%m-%d")
	useremail=cur_user.email
	userscores=cur_user.scores
	usertitle=cur_user.title
	showname=getName(request)
	isStaff=cur_user.is_staff
	accttype=cur_user.acct_type
	acctstatus=cur_user.status

	if cur_user.birth <> None and cur_user.birth <> '':
		birth = cur_user.birth.strftime("%Y-%m-%d")
	else:
		birth = '1967-01-01'

	if cur_user.sex <> None and cur_user.sex <> '':
		usersex = SEX[cur_user.sex]
	else:
		usersex = SEX[u'男']

	if cur_user.region <> None and cur_user.region <> '':
		region = cur_user.region_id
	else:
		region = '1'

	if request.GET.get('saveresult'):
		showSaveAlert = True
	else:
		showSaveAlert = False

	if request.method == 'POST':
		form = ModifyUserForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			#{'birthdt': datetime.date(1967, 1, 1), 'region': u'1', 'nickname': u'admin', 'phone': u'', 'sex': u'2'}
			user = User.objects.get(username = request.user.username)
			user.birth = cd['birth']
			user.region_id = cd['region']
			user.nickname = cd['nickname']
			user.sex = list(SEX.keys())[list(SEX.values()).index(cd['sex'])]
			user.phone = cd['phone']
			user.save()
			return HttpResponseRedirect('/myprofile/?saveresult=True')
	else:
		form = ModifyUserForm(initial={'username':request.user.username,'nickname':showname,'sex':usersex,'birth':birth,'region':region,'phone':cur_user.phone,'showSaveAlert':showSaveAlert})
	return render(request,'myprofile.html',locals())

def getName(request):
	"""页面用户名/昵称显示"""
	cur_user=User.objects.get(username=request.user.username)
	nickname=cur_user.nickname
	#如果设置了昵称，则显示昵称，否则显示账号
	if nickname <> None and nickname <> '':
		username = nickname
	else:
		username = request.user.username
	return username

def getNameByUn(usrnam):
	"""页面用户名/昵称显示"""
	cur_user=User.objects.get(username=usrnam)
	nickname=cur_user.nickname
	#如果设置了昵称，则显示昵称，否则显示账号
	if nickname <> None and nickname <> '':
		username = nickname
	else:
		username = str(usrnam)
	return username

def getUserAvatarURL(User):
	return r'/'+str(User.avatar)

@login_required
def changepwd(request):
	user=User.objects.get(username=request.user.username)
	isStaff=user.is_staff
	showname=getName(request)

	if request.method == 'POST':
		form = ChangPwdForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			newpasswd = cd['confnewpwd']
			user.set_password(newpasswd)
			user.save()
			return HttpResponseRedirect('/pwdchanged/')
	else:
		form = ChangPwdForm()
	return render(request,'passwd.html',locals())


def pwdchanged(request):
	showname=u'匿名'
	return render(request,'pwdchanged.html',locals())

@login_required
def changeavatar(request):
	user=User.objects.get(username=request.user.username)
	isStaff=user.is_staff
	showname=getName(request)
	username=request.user.username
	useravatar = getUserAvatarURL(user)

	return render(request, 'avatar.html', locals())

@login_required
def saveavatar(request):
	#ajax异步保存头像
	if request.method == 'POST' and request.is_ajax():
		data = request.POST
		img = data['avatarimg']
		#去除编码前面的字符串
		imgData=base64.b64decode(img[img.index(',')+1:])
		
		imgfname = request.user.username+'_avatar.jpg'
		dest = os.path.join(settings.STATICFILES_DIRS[0],'images','useravatars', imgfname)
		try:
			with open(dest, "wb") as destination:
				destination.write(imgData)
			user=User.objects.get(username=request.user.username)
			user.avatar = settings.STATIC_URL[1:]+'images/useravatars/'+imgfname
			user.save(update_fields=['avatar'])
			return HttpResponse("success")
		except Exception as e:
			return HttpResponseServerError()
	else:
		error_return_link_lable = u'返回'
		error_return_link = r'/changeavatar/'
		error_info_strong = u'无效访问!'
		return render(request,'innerror.html',locals())

#用户基础信息统一接口
def getUserBase(request):
	userbase={}
	user=User.objects.get(username=request.user.username)
	#是否管理员
	userbase['isStaff']=user.is_staff
	#显示账号/昵称
	userbase['showname'] = getName(request)
	#用户头像URL
	userbase['useravatar'] = getUserAvatarURL(user)
	#账号
	userbase['username'] = user.username
	#用户ID
	userbase['userid'] = user.id
	#当前积分
	userbase['userscore'] = user.scores

	return userbase

#同步用户
def syncusers(request):
	if request.user.is_superuser:
		basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		filepath = os.path.join(basedir,'members.txt')
		userlist=[]
		totl_num=0
		add_num=0
		inactive_num=0
		whitelist=['admin','user1','user3','user66']
		with open(filepath) as f:
			for line in f:
				totl_num+=1
				lstr=line.strip('\n')
				userlist.append(lstr)
				if User.objects.filter(username=lstr):
					pass
				else:
					add_num+=1
					newuser = User.objects.create_user(lstr,lstr+'@qq.com','1234abcd')
					newuser.is_staff=False
					newuser.save()
		users = User.objects.all()
		for usr in users:
			if usr.username in userlist:
				pass
			else:
				if usr.username in whitelist:
					pass
				else:
					inactive_num+=1
					usr.is_active = False
					usr.save(update_fields=['is_active'])
		return HttpResponse(u'本次同步用户已完成,其中总成员数:'+str(totl_num)+u',新增成员数:'+str(add_num)+u',取消激活成员数:'+str(inactive_num))
	else:
		return HttpResponse(u'你没有权限执行此操作')