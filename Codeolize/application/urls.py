from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    path('',homepage,name='home'),
    path('signin',signin,name='signin'),
    path('signup',signup,name='signup'),
    path('forgotpass',forgotpass,name='forgotpass'),
    path('logout',logout,name='logout'),
    path('feed',feed,name='feed'),
    path('search',search,name='search'),
    path('profile',profile,name='profile'),
    path('newpost',newpost,name='newpost'),
    path('follow',follow,name='follow'),
    path('unfollow',unfollow,name='unfollow'),
    path('followers',followers,name='followers'),
    path('following',following,name='following'),
    path('like',like,name='like'),
    path('likedisplay',likedisplay,name='likedisplay'),
    path('comment',comment,name='comment'),
    path('editprofile',editprofile,name='editprofile'),
    path('changepassword',changepassword,name='changepassword'),
    path('chatbox',chatbox,name='chatbox'),
    path('chatmessages',chatmessages,name='chatmessages'),
    path('delete',delete,name='delete'),
    path('update',update,name='update'),
    path('sendmsg',sendmsg,name='sendmsg'),
    path('picturemsg',picturemsg,name='picturemsg'),
    path('audiomsg',audiomsg,name='audioemsg'),
    path('share',share,name='share'),
    path('sharehere',sharehere,name='sharehere'),
    path('msgpost',msgpost,name='msgpost'),

    path('compiler',compiler,name='compiler'),
    path('execute',execute,name='execute'),
    path('problemlist',problemlist,name='problemlist'),
    path('problem',problem,name='problem'),
    path('problemlistsort',problemlistsort,name='problemlistsort'),
    path('solution',solution,name='solution')
]
