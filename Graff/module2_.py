from mongoengine import *
import contextlib # for urllib.urlopen()
import urllib
import os
import re

def readWebPage(url):
    #assert(url.startswith("http://"))
    with contextlib.closing(urllib.urlopen(url)) as fin:
        return fin.read()

connect("grff", host="104.47.138.204", port=3306)


class Course (Document):
    code = IntField(0,99999)
    title = StringField()
    department = StringField()
    minUnits = IntField()
    maxUnits = IntField()
    spring = IntField()
    summer = IntField()
    specialPermissionRequired = IntField()
    fall = IntField()
    prerequisites = ListField(IntField())
    corequisites = ListField(IntField())
    alternateListings = ListField(IntField())
    telp = IntField()


print Course.objects().count()

#

none = None

for course in Course.objects():
    if course.fall:
        sem = "F14"
    elif course.spring:
        sem = "S15"

    courseReturn = readWebPage("https://enr-apps.as.cmu.edu/open/SOC/SOCServlet/courseDetails?COURSE=%05d&SEMESTER=%s"%(course.code, sem))
    try:
        if "yes"==re.split(r"\<\/?dd\>", courseReturn[courseReturn.find("Special Permission Required"):])[1].lower():
            course.specialPermissionRequired = 1
        else:
            course.specialPermissionRequired = 0
    except:
        course.specialPermissionRequired = 0

    print "%05d"%course.code,
    print course.department
    prerequisites = []
    try:
        q = eval(re.sub(r"(^0)|(\s0)"," ", re.split(r"\<\/?dd\>", courseReturn[courseReturn.find("Prerequisites"):])[1].lower().replace("and",", ").replace("(0","(")))
    except:
        q = None

    if type(q)==tuple:
        for qq in q:
            try:
                prerequisites += [qq]
            except: pass
    elif q:
        try:
            prerequisites += [q]
        except: pass
    course.prerequisites = prerequisites
    print course.prerequisites
    course.telp = 1
    print course.save()
    

    

    
