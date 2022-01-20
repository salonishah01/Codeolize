from django.db import models
from django.db.models.fields import DateTimeField
from django.utils import timezone

# Create your models here.
class User(models.Model):
    name=models.CharField(max_length=200)
    profilepic=models.ImageField(default='profilepic/default.jpg',upload_to='profilepic')
    userid=models.CharField(max_length=200)
    password=models.CharField(max_length=200)
    emailid=models.CharField(max_length=200)
    postct=models.IntegerField(default=0)
    followers=models.IntegerField(default=0)
    following=models.IntegerField(default=0)
    logintime=models.DateTimeField(default=timezone.now)
    score=models.IntegerField(default=0)

    def __str__(self):
         return str(self.name)+" - "+str(self.userid)

class FndF(models.Model):
    fuserid=models.CharField(max_length=200)
    tuserid=models.CharField(max_length=200)

    def __str__(self):
        return str(self.fuserid)+" - "+str(self.tuserid)

class Post(models.Model):
    userid=models.CharField(max_length=200)
    postid=models.CharField(max_length=200)
    picture=models.ImageField(upload_to='post')
    caption=models.CharField(max_length=500)
    likecount=models.IntegerField(default=0)
    commentcount=models.IntegerField(default=0)
    datetime=models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.userid)+" - "+str(self.postid)
    
class Like(models.Model):
    postid=models.CharField(max_length=200)
    userid=models.CharField(max_length=200)

    def __str__(self):
        return str(self.userid)+" - "+str(self.postid)

class Comment(models.Model):
    postid=models.CharField(max_length=200)
    userid=models.CharField(max_length=200)
    comment=models.CharField(max_length=200)

    def __str__(self):
        return str(self.userid)+" - "+str(self.postid)

class Message(models.Model):
    fuserid=models.CharField(max_length=200)
    tuserid=models.CharField(max_length=200)
    textmessage=models.CharField(max_length=500,default='NULL')
    picturemessage=models.ImageField(upload_to='message',null=True)
    audiomessage=models.FileField(null=True)
    linkmessage=models.URLField(max_length=200,default='NULL')
    datetime=models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.fuserid)+" - "+str(self.tuserid)

class online(models.Model):
    userid=models.CharField(max_length=200)

    def __str__(self):
        return str(self.userid)

class Problem(models.Model):
    problemid=models.CharField(max_length=200)
    problemcode=models.CharField(max_length=200)
    title=models.CharField(max_length=200)
    description=models.CharField(max_length=5000)
    level=models.CharField(max_length=200)
    totalsub=models.IntegerField(default=0)
    correctsu=models.IntegerField(default=0)
    rate=models.FloatField(default=0)

    def __str__(self):
        return str(self.problemid)+" - "+str(self.title)

class UserSub(models.Model):
    userid=models.CharField(max_length=200)
    cerror=models.IntegerField(default=0)
    rerror=models.IntegerField(default=0)
    terror=models.IntegerField(default=0)
    werror=models.IntegerField(default=0)
    accept=models.IntegerField(default=0)

    def __str__(self):
        return str(self.userid)


class Submission(models.Model):
    submissionid=models.CharField(max_length=200)
    userid=models.CharField(max_length=200)
    problemid=models.CharField(max_length=200)
    problemtitle=models.CharField(max_length=200)
    score=models.IntegerField(default=0)
    status=models.CharField(max_length=200)
    timestamp=models.DateTimeField(default=timezone.now)
    time=models.IntegerField(default=0)
    memory=models.IntegerField(default=0)
    langid=models.IntegerField(default=0)
    langname=models.CharField(max_length=200)

    def __str__(self):
        return str(self.userid)+"-"+str(self.problemid)


"""

class Testcase(models.Model):
    testcaseid=models.CharField(max_length=200)
    problemid=models.CharField(max_length=200)
    inputt=models.CharField(max_length=20000)
    output=models.CharField(max_length=20000)
    typee=models.CharField(max_length=200)

    def __str__(self):
        return str(problemid)+"-"+str(testcaseid)

class Tags(models.Model):
    tagid
    tagtitle

    def __str__(self):
        return str(tagtitle)

class Problemtags(models.Model):
    problemid
    tagid

    def __str__(self):
        return str(problemid)+"-"+str(tagid)

class Constraint(models.Model):
    problemid
    language
    timelimit
    spacelimit

    def __str__(self):
        return str(problemid)+"-"+str(language)
    

class Record(models.Model):
    recordid
    submissionid
    problemid
    testacaseid
    status

    def __str__(self):
        return str(problemid)+"-"+str(testacaseid)

"""