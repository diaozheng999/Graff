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
    fall = IntField()
    prerequisites = ListField(ReferenceField('Course'))
    corequisites = ListField(ReferenceField('Course'))
    alternateListings = ListField(ReferenceField('Course'))



deptMap = {
           31: 'Aerospace Studies-ROTC',
           48: 'Architecture',
           60: 'Art',
           52: 'BXA Intercollege Degree Prorams',
           3: 'Biological Sciences',
           42: 'Biomedical Engineering',
           70: 'Business Administration',
           62: 'CFA Interdisciplinary',
           39: 'CIT Interdisciplinary',
           99: 'Carnegie Mellon University-Wide Studies',
           64: 'Center for the Arts in Society',
           86: 'Center for the Neural Basis of Cognition',
           6: 'Chemical Engineering',
           9: 'Chemistry',
           12: 'Civil & Environmental Engineering',
           2: 'Computational Biology',
           15: 'Computer Science',
           62: 'Computer Science and Arts',
           93: 'Creative Enterprise: School of Public Policy and Management',
           51: 'Design',
           67: 'Dietrich college Information Science',
           66: 'Dietrich College Interdisciplinary',
           54: 'Drama',
           73: 'Economics',
           18: 'Electrical & Computer Engineering',
           20: 'Electronic Commerce',
           19: 'Engineering & Public Policy',
           76: 'English',
           53: 'Entertainment Technology Pittsburgh',
           65: 'General Dietrich College',
           94: 'Heinz College Wide Courses',
           79: 'History',
           5: 'Human-Computer Interaction',
           62: 'Humanities and Arts',
           4: 'Information & Communication Technology',
           14: 'Information Networking Institute',
           95: 'Information Systems: sch of IS & Mgmt',
           8: 'Institute for Software Research',
           49: 'Integrated Innovation Institute',
           11: 'Language Technologies Institute',
           38: 'MCS Interdisciplinary',
           10: 'Machine Learning',
           27: 'Material Science & Engineering',
           21: 'Mathematical Sciences',
           24: 'Mechanical Engineering',
           92: 'Medical Management : Sch of Pub Pol & Mgt',
           30: 'Mility Science-ROTC',
           82: 'Modern Languages',
           57: 'Music',
           32: 'Naval Science-ROTC',
           80: 'Philosophy',
           69: 'Physical Education',
           33: 'Physics',
           85: 'Psychology',
           91: 'Public Mnagement : Sch of Pub Pol & Mgt',
           90: 'Public Policy : Sch of Pub Pol & Mgt',
           16: 'Robotics',
           62: 'Science and Arts',
           96: 'Silicon Valley',
           88: 'Social & Decision Sciences',
           17: 'Software Engineering',
           36: 'Statistics',
           98: 'StuCo (Student Led Courses)',
           45: 'Tepper School of Business',
           46: 'Tepper School of Business',
           47: 'Tepper School of Business'
           }



def parseCourse(course, season):
    global deptMap
    for n in course.split("<TR>"):
        if "NOWRAP" not in n[:10]: continue

        p = [q[q.rfind(">")+1:q.rfind("<")] for q in n.split("/TD")]
        print p[0],
        if Course.objects(code=int(p[0])).count()>0:
            for course in Course.objects(code=int(p[0])):
                n = course
                break;
            if season == "spring":
                n.spring = 1
            elif season == "summer":
                n.summer = 1
            elif season == "fall":
                n.fall = 1
            print n.save()
            continue;
        

        n = Course()
        n.code = int(p[0])
        n.department = deptMap[n.code/1000]
        n.title = p[1]

        n.spring = 0
        n.summer = 0
        n.fall = 0

        if "," in p[2] or "-" in p[2]:
            try:
                L = [int(float(q)) for q in re.split(r'[\s,-]',p[2]) if q!=""]
            except:
                print p[2]
            n.minUnits = min(L)
            n.maxUnits = max(L)
        elif p[2]=='VAR':
            n.minUnits = 0;
            n.maxUnits = 0;
        else:
            n.minUnits = int(float(p[2]))
            n.maxUnits = int(float(p[2]))

        if season == "spring":
            n.spring = 1
        elif season == "summer":
            n.summer = 1
        elif season == "fall":
            n.fall = 1
        print n.save()


course = readWebPage("https://enr-apps.as.cmu.edu/assets/SOC/sched_layout_fall.htm")
parseCourse(course, "fall")
course = readWebPage("https://enr-apps.as.cmu.edu/assets/SOC/sched_layout_spring.htm")
parseCourse(course, "spring")