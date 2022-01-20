from django.contrib.messages.api import warning
from django.shortcuts import render
from .models import User,Post,FndF,Comment,Like,Message,online,Problem,UserSub,Submission
from django.forms import ModelForm
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils import timezone
import random
from sphere_engine import CompilersClientV4
from sphere_engine import ProblemsClientV4
from sphere_engine.exceptions import SphereEngineException
import urllib.request
import requests
from django.utils.html import format_html

problemaccessToken='5ece9a4c10e76d352a0a8d16f3992a18'
problemendpoint='bd09cdcb.problems.sphere-engine.com'

compileraccessToken='375785224f4bdcc4a8846edbfa1bf0ac'
compilerendpoint='bd09cdcb.compilers.sphere-engine.com'

client = CompilersClientV4(compileraccessToken,compilerendpoint)
problemclient = ProblemsClientV4(problemaccessToken,problemendpoint)

# Create your views here.
def homepage(request):
    return render(request,'homepage.html',{'signin':1})

def logout(request):
    user=User.objects.get(userid=request.session['userid'])
    user.logintime=timezone.now()
    user.save()
    for each in online.objects.all():
        if(each.userid==user.userid):
            each.delete()
    del request.session['name']
    del request.session['userid']
    return render(request,'homepage.html',{'signin':1})

def myfun(e):
    return e.datetime

def signin(request):
    if request.method=="POST":
        username=request.POST.get('username')
        cpassword=request.POST.get('pass')
        if(username=='' or cpassword==''):
            messages.warning(request,f'Fields Cannot be Empty!')
            return render(request,'homepage.html',{'signin':1})
        obj=User.objects.all()
        for each in obj:
            if(each.userid==username and each.password==cpassword):
                request.session['userid']=each.userid
                request.session['name']=each.name
                each.logintime=timezone.now()
                each.save()
                allfollowers=FndF.objects.filter(fuserid=username)
                allpost=Post.objects.all()
                online(userid=username).save()
                post=[]
                for each1 in allpost:
                    for every in allfollowers:
                        if(each1.userid==every.tuserid):
                            post.append(each1)
                if(len(post)==0):      
                    messages.warning(request,f'Please Add some friends!')
                like=[]
                for each1 in Like.objects.all():
                    if(each1.userid==username):
                        like.append(each1.postid)
                post.sort(reverse=True,key=myfun)
                print(each.profilepic)
                return render(request,'userhome.html',{'user':each,'posts':post,'alluser':obj,'comment':Comment.objects.all(),'like':like}) 
        messages.warning(request,f'No Matching User Found!')        
        return render(request,'homepage.html',{'signin':1})
    return render(request,'homepage.html',{'signin':1})

class UserForm(ModelForm):
    class Meta:
        model=User
        fields=['name','profilepic','userid','password','emailid']

def signup(request):
    if request.method=="POST":
        curname=request.POST.get('name')
        curmail=request.POST.get('emailid')
        curusername=request.POST.get('userid')
        curpass=request.POST.get('password')
        currepass=request.POST.get('repass')
        if(curname=='' or curmail=='' or curusername=='' or curpass=='' or currepass==''):
            messages.warning(request,f'Fields Cannot be Empty!')
            return render(request,'homepage.html',{'signin':0})
        if(curpass != currepass):
            messages.warning(request,f'Passwords Donot Match!')
            return render(request,'homepage.html',{'signin':0})
        obj=User.objects.all()
        for each in obj:
            if(each.userid==curusername):
                messages.warning(request,f'Duplicate Username Found!')
                return render(request,'homepage.html',{'signin':0})
        form=UserForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
        messages.success(request,f'Registration Successful!')
        UserSub(userid=curusername).save()
        return render(request,'homepage.html',{'signin':1})
    return render(request,'homepage.html',{'signin':0})

def forgotpass(request):
    if request.method=="POST":
        curmail=request.POST.get('emailid')
        curusername=request.POST.get('userid')
        curpass=request.POST.get('password')
        currepass=request.POST.get('repass')
        if(curmail=='' or curusername=='' or curpass=='' or currepass==''):
            messages.warning(request,f'Fields Cannot be Empty!')
            return render(request,'forgotpass.html')
        if(curpass != currepass):
            messages.warning(request,f'Passwords Donot Match!')
            return render(request,'forgotpass.html')
        obj=User.objects.all()
        for each in obj:
            if(each.userid==curusername and each.emailid==curmail):
                each.password=curpass
                each.save()
                messages.success(request,f'Password Updated Successfully!')
                return render(request,'homepage.html',{'signin':1})
        messages.warning(request,f'No Matching User Found!')
        return render(request,'forgotpass.html')
    return render(request,'forgotpass.html')

def feed(request):
    obj=User.objects.all()
    userid=request.session.get('userid')
    curuser=User.objects.all().filter(userid=request.session.get('userid'))[0]
    print(curuser.name)
    name=request.session.get('name')
    allfollowers=FndF.objects.filter(fuserid=userid)
    allpost=Post.objects.all()
    post=[]
    for each in allpost:
        for every in allfollowers:
            if(each.userid==every.tuserid):
                post.append(each)
    if(len(post)==0):      
        messages.warning(request,f'Nothing to show!')
    like=[]
    for each in Like.objects.all():
        if(each.userid==userid):
            like.append(each.postid)
    post.sort(reverse=True,key=myfun)
    return render(request,'userhome.html',{'user':curuser,'posts':post,'alluser':obj,'comment':Comment.objects.all(),'like':like})

def search(request):
    if request.method=="POST":
        userid=request.POST.get('userid')
        if(userid==''):
            messages.warning(request,f'Field cannot be empty!')
            return feed(request)
        obj=User.objects.all()
        curuserid=request.session.get('userid')
        curname=request.session.get('name')
        list1=[]
        for each in obj:
            if(each.userid==userid and each.userid!=curuserid):
                list1.append(each)
        if(len(list1)==0):
            messages.warning(request,f'No Matching User Found!')
            return feed(request)
        userposts=[]
        for each in Post.objects.all():
            if(each.userid==list1[0].userid):
                userposts.append(each)
        followers=FndF.objects.filter(fuserid=curuserid,tuserid=userid)
        like=[]
        for each in Like.objects.all():
            if(each.userid==curuserid):
                like.append(each.postid)
        messages.success(request,f'Search Result')
        userposts.sort(reverse=True,key=myfun)
        userstats=UserSub.objects.filter(userid=userid)[0]
        submissions=Submission.objects.filter(userid=userid)
        return render(request,'profile.html',{'userid':curuserid,'name':curname,'profile':list1[0],'posts':userposts,'alluser':obj,'status':len(followers),'comment':Comment.objects.all(),'like':like,'userstats':userstats,'subs':submissions})

def profile(request):
    profileid=request.GET.get('profileid')
    userprofile=User.objects.filter(userid=profileid)
    userposts=[]
    for each in Post.objects.all():
        if(each.userid==profileid):
            userposts.append(each)
    userid=request.session.get('userid')
    name=request.session.get('name')
    followers=FndF.objects.filter(fuserid=userid,tuserid=userprofile[0].userid)
    like=[]
    for each in Like.objects.all():
        if(each.userid==userid):
            like.append(each.postid)
    userposts.sort(reverse=True,key=myfun)
    userstats=UserSub.objects.filter(userid=profileid)[0]
    submissions=Submission.objects.filter(userid=profileid)
    return render(request,'profile.html',{'userid':userid,'name':name,'profile':userprofile[0],'posts':userposts,'alluser':User.objects.all(),'status':len(followers),'comment':Comment.objects.all(),'like':like,'userstats':userstats,'subs':submissions})

class PostForm(ModelForm):
    class Meta:
        model=Post
        fields=['picture','caption']

def newpost(request):
    if request.method=="POST":
        userid=request.session.get('userid')
        name=request.session.get('name')
        user=User.objects.all()
        for each in user:
            if(each.userid==userid):
                each.postct+=1
                each.save()
                curpostid=str(each.userid)+str(random.randint(0,2000))
                while len(Post.objects.filter(postid=curpostid))!=0:
                    curpostid=str(each.userid)+str(random.randint(10,2000))
                curpost=Post(userid=userid,postid=curpostid)
                form=PostForm(request.POST,request.FILES,instance=curpost)
                if form.is_valid():
                    form.save()
                messages.success(request,f'Post Created!')      
                return feed(request)
    userid=request.session.get('userid')
    name=request.session.get('name')
    return render(request,'newpost.html',{'userid':userid,'name':name,})

def follow(request):
    fuserid=request.GET.get('userid')
    tuserid=request.GET.get('profileid')
    FndF(fuserid=fuserid,tuserid=tuserid).save()
    user1=User.objects.get(userid=fuserid)
    user2=User.objects.get(userid=tuserid)
    user1.following+=1
    user1.save()
    user2.followers+=1
    user2.save()
    return profile(request)

def unfollow(request):
    fuserid=request.GET.get('userid')
    tuserid=request.GET.get('profileid')
    obj1=FndF.objects.get(fuserid=fuserid,tuserid=tuserid)
    obj1.delete()
    user1=User.objects.get(userid=fuserid)
    user2=User.objects.get(userid=tuserid)
    user1.following-=1
    user1.save()
    user2.followers-=1
    user2.save()
    return profile(request)

def followers(request):
    userid=request.GET.get('userid')
    curuserid=request.session.get('userid')
    curname=request.session.get('name')
    allfollow=FndF.objects.all()
    obj1=User.objects.all()
    follows=[]
    for each in allfollow:
        if(each.tuserid==userid):
            for every in obj1:
                if(each.fuserid==every.userid):
                    follows.append(every)
    if(len(follows)==0):
        messages.warning(request,f'No Followers Found!')
    else:
        messages.success(request,f'Followers List')
    return render(request,'searchresult.html',{'userid':curuserid,'name':curname,'search':follows})

def following(request):
    userid=request.GET.get('userid')
    curuserid=request.session.get('userid')
    curname=request.session.get('name')
    allfollow=FndF.objects.all()
    obj1=User.objects.all()
    follows=[]
    for each in allfollow:
        if(each.fuserid==userid):
            for every in obj1:
                if(each.tuserid==every.userid):
                    follows.append(every)
    if(len(follows)==0):
        messages.warning(request,f'No Followings Found!')
    else:
        messages.success(request,f'Following List')
    return render(request,'searchresult.html',{'userid':curuserid,'name':curname,'search':follows})

def like(request):
    curpostid=request.GET.get('postid')
    curuserid=request.session.get('userid')
    like=Like.objects.filter(postid=curpostid,userid=curuserid)
    post=Post.objects.get(postid=curpostid)
    if(len(like)==0):
        Like(postid=curpostid,userid=curuserid).save()
        post.likecount+=1
        post.save()
    else:
        like.delete()
        post.likecount-=1
        post.save()
    return feed(request)

def likedisplay(request):
    curuserid=request.session.get('userid')
    curname=request.session.get('name')
    curpostid=request.GET.get('postid')
    like=Like.objects.filter(postid=curpostid)
    user=User.objects.all()
    obj1=[]
    for each in like:
        for every in user:
            if(each.userid==every.userid):
                obj1.append(every)
    if(len(obj1)==0):
        messages.warning(request,f'No Likes Found!')
    else:
        messages.success(request,f'Liked by following users')
    return render(request,'searchresult.html',{'userid':curuserid,'name':curname,'search':obj1})

def comment(request):
    curuserid=request.session.get('userid')
    curpostid=request.POST.get('postid')
    comment=request.POST.get('comment')
    post=Post.objects.get(postid=curpostid)
    post.commentcount+=1
    post.save()
    Comment(postid=curpostid,userid=curuserid,comment=comment).save()
    return feed(request)


class UpdatedUserForm(ModelForm):
    class Meta:
        model=User
        fields=['profilepic']

def editprofile(request):
    if request.method=="POST":
        curuserid=request.POST.get('userid')
        newemail=request.POST.get('emailid')
        newname=request.POST.get('name')
        status=request.POST.get('status')
        user=User.objects.get(userid=curuserid)
        user.name=newname
        request.session['name']=newname
        user.emailid=newemail
        user.save()
        if(status):
            form=UpdatedUserForm(request.POST,request.FILES,instance=user)
            if form.is_valid():
                form.save()
        messages.success(request,f'Profile Update Successfully!')
        return feed(request)
    curuserid=request.session.get('userid')
    curname=request.session.get('name')
    user=User.objects.get(userid=curuserid)
    return render(request,'editprofile.html',{'userid':curuserid,'name':curname,'profile':user})

def changepassword(request):
    if request.method=="POST":
        curuserid=request.session.get('userid')
        curname=request.session.get('name')
        oldpass=request.POST.get('curpass')
        newpass=request.POST.get('newpass')
        repass=request.POST.get('repass')
        if(oldpass=='' or newpass=='' or repass==''):
            messages.warning(request,f'Fields cannot be empty!')
            return render(request,'changepassword.html',{'userid':curuserid})
        if(newpass!=repass):
            messages.warning(request,f'New Passwords donnot match!')
            return render(request,'changepassword.html',{'userid':curuserid})
        user=User.objects.get(userid=curuserid)
        if(user.password!=oldpass):
            messages.warning(request,f'Old Password Donnot match!')
            return render(request,'changepassword.html',{'userid':curuserid})
        user.password=newpass
        user.save()    
        messages.success(request,f'Password Updated Successfully!')
        return feed(request)
    curuserid=request.POST.get('userid')
    curname=request.POST.get('name')
    return render(request,'changepassword.html',{'userid':curuserid,'name':curname})

def chatbox(request):
    curuserid=request.session.get('userid')
    curname=request.session.get('name')
    list=[]
    for each in FndF.objects.filter(fuserid=curuserid):
        obj=FndF.objects.filter(fuserid=each.tuserid,tuserid=curuserid)
        for every in obj:
            list.append(User.objects.get(userid=every.fuserid))
    if(len(list)==0):
        messages.warning(request,f'No Connected Friends Found!')
        return feed(request)
    onlineusers=[]
    for each in online.objects.all():
        onlineusers.append(each.userid)
    return render(request,'chatbox.html',{'userid':curuserid,'name':curname,'friends':list,'status':0,'online':onlineusers})  

def chatmessages(request):
    profileid=request.GET.get('profileid')
    curuserid=request.session.get('userid')
    curname=request.session.get('name')
    Chat=[]
    for each in Message.objects.all():
        if(each.fuserid==profileid and each.tuserid==curuserid):
            Chat.append(each)
        if(each.tuserid==profileid and each.fuserid==curuserid):
            Chat.append(each)
    list=[]
    for each in FndF.objects.filter(fuserid=curuserid):
        obj=FndF.objects.filter(fuserid=each.tuserid,tuserid=curuserid)
        for every in obj:
            list.append(User.objects.get(userid=every.fuserid))
    Chat.sort(key=myfun)
    onlineusers=[]
    for each in online.objects.all():
        onlineusers.append(each.userid)
    return render(request,'chatbox.html',{'userid':curuserid,'name':curname,'friends':list,'status':1,'message':Chat,'recipient':User.objects.get(userid=profileid),'online':onlineusers})

def delete(request):
    postid=request.GET.get('postid')
    post=Post.objects.get(postid=postid)
    post.delete()  
    for each in Like.objects.all():
        if each.postid==postid:
            each.delete()
    for each in Comment.objects.all():
        if each.postid==postid:
            each.delete()
    user=User.objects.get(userid=request.session.get('userid'))
    user.postct-=1
    user.save()
    messages.success(request,f'Post Deleted Succesfully!')
    return profile(request)

def update(request):
    if request.method=="POST":
        postid=request.POST.get('postid')
        caption=request.POST.get('caption')
        post=Post.objects.get(postid=postid)
        post.caption=caption
        post.save()
        messages.success(request,f'Caption Updated!')
        
        curuserid=request.session.get('userid')
        curname=request.session.get('name')
        userprofile=User.objects.filter(userid=curuserid)
        userposts=[]
        for each in Post.objects.all():
            if(each.userid==curuserid):
                userposts.append(each)
        followers=FndF.objects.filter(fuserid=curuserid,tuserid=userprofile[0].userid)
        like=[]
        for each in Like.objects.all():
            if(each.userid==curuserid):
                like.append(each.postid)
        userposts.sort(reverse=True,key=myfun)
        userstats=UserSub.objects.filter(userid=profileid)[0]
        submissions=Submission.objects.filter(userid=curuserid)
        return render(request,'profile.html',{'userid':curuserid,'name':curname,'profile':userprofile[0],'posts':userposts,'alluser':User.objects.all(),'status':len(followers),'comment':Comment.objects.all(),'like':like,'userstats':userstats,'subs':submissions})
    postid=request.GET.get('postid')
    return render(request,'updatepost.html',{'postid':postid})

def sendmsg(request):
    message=request.POST.get('message')
    profileid=request.POST.get('profileid')
    curuserid=request.session.get('userid')
    curname=request.session.get('name')
    if(message!=''):
        Message(fuserid=curuserid,tuserid=profileid,textmessage=message).save()
    Chat=[]
    for each in Message.objects.all():
        if(each.fuserid==profileid and each.tuserid==curuserid):
            Chat.append(each)
        if(each.tuserid==profileid and each.fuserid==curuserid):
            Chat.append(each)
    list=[]
    for each in FndF.objects.filter(fuserid=curuserid):
        obj=FndF.objects.filter(fuserid=each.tuserid,tuserid=curuserid)
        for every in obj:
            list.append(User.objects.get(userid=every.fuserid))
    Chat.sort(key=myfun)
    onlineusers=[]
    for each in online.objects.all():
        onlineusers.append(each.userid)
    return render(request,'chatbox.html',{'userid':curuserid,'name':curname,'friends':list,'status':1,'message':Chat,'recipient':User.objects.get(userid=profileid),'online':onlineusers})

class MsgForm(ModelForm):
    class Meta:
        model=Message
        fields=['picturemessage']

def picturemsg(request):
    if request.method=="POST":
        profileid=request.POST.get('profileid')
        msg=Message(fuserid=request.session.get('userid'),tuserid=profileid)
        form=MsgForm(request.POST,request.FILES,instance=msg)
        if(form.is_valid()):
            form.save()
        curuserid=request.session.get('userid')
        curname=request.session.get('name')
        Chat=[]
        for each in Message.objects.all():
            if(each.fuserid==profileid and each.tuserid==curuserid):
                Chat.append(each)
            if(each.tuserid==profileid and each.fuserid==curuserid):
                Chat.append(each)
        list=[]
        for each in FndF.objects.filter(fuserid=curuserid):
            obj=FndF.objects.filter(fuserid=each.tuserid,tuserid=curuserid)
            for every in obj:
                list.append(User.objects.get(userid=every.fuserid))
        Chat.sort(key=myfun)
        onlineusers=[]
        for each in online.objects.all():
            onlineusers.append(each.userid)
        return render(request,'chatbox.html',{'userid':curuserid,'name':curname,'friends':list,'status':1,'message':Chat,'recipient':User.objects.get(userid=profileid),'online':onlineusers})
    profileid=request.GET.get('profileid')
    return render(request,'picturemsg.html',{'profileid':profileid})


class MsgFormNew(ModelForm):
    class Meta:
        model=Message
        fields=['audiomessage']

def audiomsg(request):
    if request.method=="POST":
        profileid=request.POST.get('profileid')
        msg=Message(fuserid=request.session.get('userid'),tuserid=profileid)
        form=MsgFormNew(request.POST,request.FILES,instance=msg)
        if(form.is_valid()):
            form.save()
        
        curuserid=request.session.get('userid')
        curname=request.session.get('name')
        Chat=[]
        for each in Message.objects.all():
            if(each.fuserid==profileid and each.tuserid==curuserid):
                Chat.append(each)
            if(each.tuserid==profileid and each.fuserid==curuserid):
                Chat.append(each)
        list=[]
        for each in FndF.objects.filter(fuserid=curuserid):
            obj=FndF.objects.filter(fuserid=each.tuserid,tuserid=curuserid)
            for every in obj:
                list.append(User.objects.get(userid=every.fuserid))
        Chat.sort(key=myfun)
        onlineusers=[]
        for each in online.objects.all():
            onlineusers.append(each.userid)
        return render(request,'chatbox.html',{'userid':curuserid,'name':curname,'friends':list,'status':1,'message':Chat,'recipient':User.objects.get(userid=profileid),'online':onlineusers})
    profileid=request.GET.get('profileid')
    return render(request,'audiomsg.html',{'profileid':profileid})

def share(request):
    postid=request.GET.get('postid')
    curuserid=request.session.get('userid')
    curname=request.session.get('name')
    list=[]
    for each in FndF.objects.filter(fuserid=curuserid):
        obj=FndF.objects.filter(fuserid=each.tuserid,tuserid=curuserid)
        for every in obj:
            list.append(User.objects.get(userid=every.fuserid))
    if(len(list)==0):
        messages.warning(request,f'No Connected Friends Found!')
        return feed(request)
    return render(request,'share.html',{'userid':curuserid,'name':curname,'friends':list,'postid':postid})  

def sharehere(request):
    userid=request.session.get('userid')
    profileid=request.GET.get('profileid')
    postid=request.GET.get('postid')
    post=Post.objects.get(postid=postid)
    msg=''
    msg='Here is a post by '+User.objects.get(userid=post.userid).name+'. Click to Open!'
    link='/msgpost?postid='+postid
    Message(fuserid=userid,tuserid=profileid,picturemessage=post.picture,textmessage=msg,linkmessage=link).save()
    messages.success(request,f'Message Sent')
    return feed(request)

def msgpost(request):
    postid=request.GET.get('postid')
    post=Post.objects.get(postid=postid)
    newuser=User.objects.get(userid=post.userid)
    status=False
    for each in Like.objects.all():
        if(each.userid==request.session.get('userid') and each.postid==postid):
            status=True
    return render(request,'post.html',{'userid':request.session.get('userid'),'name':request.session.get('name'),'newuser':newuser,'post':post,'like':status,'comment':Comment.objects.all()})


def compiler(request):
    curuser=User.objects.all().filter(userid=request.session.get('userid'))[0]
    try:
        response1 = client.test()
    except SphereEngineException as e:
        if e.code == 401:
            messages.warning(request,f'Oops there is some problem with the compiler!')
    try:
        response2 = client.compilers()
    except SphereEngineException as e:
        if e.code == 401:
            messages.warning(request,f'Invalid access token!')
    languagelist=[]
    for each in response2['items']:
        languagelist.append({'id':each['id'],'name':each['name']})

    problemid=request.GET.get('problemid')
    problemstatus=0
    if(problemid!="false"):
        problemstatus=1
    print(problemid)
    curlanguage={"id":-1,"name":"-- select the compiler --"}
    return render(request,'compiler.html',{'user':curuser,'language':languagelist,'isproblem':problemstatus,'problemid':problemid,'code':'','input':'','output':'','curlan':curlanguage})

def execute(request):
    if 'run' in request.POST:
        curuser=User.objects.all().filter(userid=request.session.get('userid'))[0]
        language=request.POST.get('language')
        code=request.POST.get('code')
        inputt=request.POST.get('input')
        status=request.POST.get('custominput')
    
        try:
            compiler = client.submissions.create(code, language, inputt)
        except SphereEngineException as e:
            if e.code == 401:
                print('Invalid access token')
            elif e.code == 402:
                print('Unable to create submission')
            elif e.code == 400:
                print('Error code: ' + str(e.error_code) + ', details available in the message: ' + str(e))
        
        while True:
            try:
                submission = client.submissions.get(compiler['id'])
                if not submission['executing']:
                    break
            except SphereEngineException as e:
                if e.code == 401:
                    print('Invalid access token')
                elif e.code == 403:
                    print('Access to the submission is forbidden')
                elif e.code == 404:
                    print('Submission does not exist')
        statuscode=submission['result']['status']['code']
        urll=''
        if statuscode==15:
            urll=submission['result']['streams']['output']['uri']
        else:
            urll=submission['result']['streams']['cmpinfo']['uri']
        responsee = urllib.request.urlopen(urll)
        html = str(responsee.read())
        output=html[2:len(html)-1]

        try:
            response2 = client.compilers()
        except SphereEngineException as e:
            if e.code == 401:
                messages.warning(request,f'Invalid access token!')
        languagelist=[]
        for each in response2['items']:
            languagelist.append({'id':each['id'],'name':each['name']})
        problemid=request.POST.get('problemid')
        problemstatus=0
        if(problemid!="false"):
            problemstatus=1
        print(problemid)
        curlanguage={}
        for each in languagelist:
            if str(each['id'])==str(language):
                curlanguage=each
                break
        return render(request,'compiler.html',{'user':curuser,'language':languagelist,'isproblem':problemstatus,'problemid':problemid,'code':code,'input':inputt,'output':output,'curlan':curlanguage})
    else:
        curuser=User.objects.all().filter(userid=request.session.get('userid'))[0]
        language=request.POST.get('language')
        code=request.POST.get('code')
        problemid=request.POST.get('problemid')
        try:
            compiler = problemclient.submissions.create(problemid,code,language)
        except SphereEngineException as e:
            if e.code == 401:
                messages.warning(request,f'Invalid access token')
            elif e.code == 402:
                messages.warning(request,f'Unable to create submission')
            elif e.code == 400:
                messages.warning(request,f'Error code: ' + str(e.error_code) + ', details available in the message: ' + str(e))
        
        while True:
            try:
                submission = problemclient.submissions.get(compiler['id'])
                if not submission['executing']:
                    break
            except SphereEngineException as e:
                if e.code == 401:
                    messages.warning(request,f'Invalid access token')
                elif e.code == 403:
                    messages.warning(request,f'Access to the submission is forbidden')
                elif e.code == 404:
                    messages.warning(request,f'Submission does not exist')

        status=submission['result']['status']['name']
        score=submission['result']['score']
        compilername=submission['compiler']['name']
        time=submission['result']['time']
        memory=submission['result']['memory']
        title=submission['problem']['name']
        
        point={'Easy':1,'Medium':2,'Hard':3}

        if(submission['result']['status']['code']==15):
            messages.success(request,status)
            curuser.score=curuser.score+point[Problem.objects.filter(problemid=problemid)[0].level]
            curuser.save()
        else:
            messages.warning(request,status)

        curuser.score=curuser.score+point[Problem.objects.filter(problemid=problemid)[0].level]
        curuser.save()

        Submission(submissionid=compiler['id'],userid=curuser.userid,problemid=problemid,problemtitle=title,score=score,status=status,time=time,memory=memory,langid=language,langname=compilername).save()
        
        curusersubmission=UserSub.objects.filter(userid=curuser.userid)
        if(len(curusersubmission)==0):
            UserSub(userid=curuser.userid).save()
        
        curusersubmission=UserSub.objects.filter(userid=curuser.userid)[0]
        if(submission['result']['status']['code']==11):
            curusersubmission.cerror+=1
        elif(submission['result']['status']['code']==13):
            curusersubmission.terror+=1
        elif(submission['result']['status']['code']==14):
            curusersubmission.werror+=1
        elif(submission['result']['status']['code']==15):
            curusersubmission.accept+=1
        else:
            curusersubmission.rerror+=1
        curusersubmission.save()
        
        curproblem=Problem.objects.filter(problemid=problemid)[0]
        curproblem.totalsub+=1
        if(submission['result']['status']['code']==15):
            curproblem.correctsu+=1
        curproblem.rate=((curproblem.correctsu*100)/curproblem.totalsub)
        curproblem.save()

        try:
            response2 = client.compilers()
        except SphereEngineException as e:
            if e.code == 401:
                messages.warning(request,f'Invalid access token!')
        languagelist=[]
        for each in response2['items']:
            languagelist.append({'id':each['id'],'name':each['name']})
        problemstatus=0
        if(problemid!="false"):
            problemstatus=1
        curlanguage={}
        for each in languagelist:
            if str(each['id'])==str(language):
                curlanguage=each
                break
        
        return render(request,'compiler.html',{'user':curuser,'language':languagelist,'isproblem':problemstatus,'problemid':problemid,'code':code,'input':'','output':'','curlan':curlanguage})
        
def problemlist(request):
    curuser=User.objects.all().filter(userid=request.session.get('userid'))[0]
    problems=Problem.objects.all()
    return render(request,'problemlist.html',{'user':curuser,'problem':problems})


def problem(request):
    problemid=request.GET.get('problemid')
    curproblem=Problem.objects.filter(problemid=problemid)[0]
    curproblem.description=format_html(curproblem.description)
    curuser=User.objects.all().filter(userid=request.session.get('userid'))[0]
    submissions=Submission.objects.filter(problemid=problemid)
    return render(request,'problem.html',{'user':curuser,'problem':curproblem,'subs':submissions})


def problemlistsort(request):
    curuser=User.objects.all().filter(userid=request.session.get('userid'))[0]
    problems=Problem.objects.all()
    easy=0
    medium=0
    hard=0
    for each in problems:
        if each.level=="Easy":
            easy+=1
        elif each.level=="Medium":
            medium+=1
        else:
            hard+=1
    print(easy,medium,hard)
    return render(request,'problemsort.html',{'user':curuser,'problem':problems})

def solution(request):
    submissionid=request.GET.get('submissionid')
    cursub=Submission.objects.filter(submissionid=submissionid)[0]
    curuser=User.objects.filter(userid=request.session.get('userid'))[0]

    try:
        response = problemclient.submissions.get(submissionid)
    except SphereEngineException as e:
        if e.code == 401:
            print('Invalid access token')
        elif e.code == 403:
            print('Access to the submission is forbidden')
        elif e.code == 404:
            print('Submission does not exist')
    testcase=response['result']['testcases']
    print(testcase)
    code=problemclient.submissions.getSubmissionFile(submissionid,'source')
    return render(request,'solution.html',{'user':curuser,'sub':cursub,'code':code,'testcase':testcase})