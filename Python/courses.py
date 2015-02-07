
import random
from Tkinter import *
from math import *
from eventBasedAnimationClass import EventBasedAnimationClass

width = 800
controlsWidth = 200
height = 600
cx,cy = width/2, height/2
scale = 1
repulsionConstant = 1000000.0
electronRepulsionConstant = 200000.0
hookesLawK = 0.1
r = 25


testCourseNumber = 1

class Electron(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.ax = 0
        self.ay = 0

    def getCoords(self):
        return (self.x, self.y)

    def doPhysics(self):
        aLimit = 10
        self.ax = max(min(self.ax, aLimit), -aLimit)
        self.ay = max(min(self.ay, aLimit), -aLimit)
        #self.ax *= 0.9
        #self.ay *= 0.9

        self.vx += self.ax
        self.vy += self.ay
        #self.vx = max(min(self.vx, 10), -10)
        #self.vy = max(min(self.vy, 10), -10)
        self.vx *= 0.7
        self.vy *= 0.7

        self.x += self.vx
        self.x = max(min(self.x, width-0.1), 0.1)
        self.y += self.vy
        self.y = max(min(self.y, height-0.1), 0.1)

    def __repr__(self):
        return "Electron at %f %f" % (self.x, self.y)

    def __eq__(self, other):
        epsilon = 0.1
        return abs(self.x-other.x) < epsilon and abs(self.y-other.y) < epsilon

class Course(object):
    def __init__(self, courseNumber, status=0, courseName="", prereqs = ()):
        # Takes in strings courseNumber, courseName and list of courses prereqs
        # Should prereqs be a tuple of strings of course numbers
        self.courseNumber = courseNumber
        self.courseName = courseName
        self.prereqs = prereqs
        self.status = status # 0 = not taken, 1 = taken, 2 = taking

    def __str__(self):
        return "%s: %s" % (self.courseNumber, self.courseName)

    def __eq__(self, other):
        return self.courseNumber == other.courseNumber

class CourseCatalog(object):
    def __init__(self):
        pass




def getNextCoordinate(coordinate):
    # Takes in tuple coordinate
    # Returns tuple next coordinate
    x,y = coordinate

    if (x > 0 and x == y) or (x > abs(y)): # Move down
        return (x,y-1)
    if x <= 0 and abs(y) <= abs(x): # Move up
        return (x,y+1)
    if y < 0 and abs(x) <= abs(y): # Move left
        return (x-1, y)
    if y > 0 and abs(x) < y: # Move right
        return (x+1, y)





class EventBasedAnimationDemo(EventBasedAnimationClass):

    def __init__(self):

        super(EventBasedAnimationDemo, self).__init__(width + controlsWidth, height)

        self.timerDelay = 25

        self.courses = [Course("15-112", 1, "Fundamentals of Programming and Computer Science", ())]

        self.electrons = [Electron(cx,cy)]
        self.shapeSelected = False

        self.completedCourses = 1

    
    def onMousePressed(self, event):
        self.pressCoordinates = (event.x, event.y)
        shapesSelected = self.canvas.find_withtag(CURRENT)
        if len(shapesSelected) > 0:
            self.shapeSelected = True
            self.indexOfElectronSelected = self.electrons.index(Electron(*self.canvas.coords(shapesSelected[0])))
        else:
            self.shapeSelected = False

    def onTimerFired(self):
        if not self.shapeSelected:

            # Set all accelerations to 0
            for electron in self.electrons:
                electron.ax = 0
                electron.ay = 0        

            # Process physics
            for i in xrange(len(self.electrons)):
                electron = self.electrons[i]

                # Set electron's ax and ay
                # Wall's repulsions
                electron.ax += copysign(1,electron.x) * (repulsionConstant/(electron.x)**2 + copysign(1,electron.x - width) * repulsionConstant/(electron.x - width)**2)
                electron.ay += copysign(1,electron.y) * (repulsionConstant/(electron.y)**2 + copysign(1,electron.y - height) * repulsionConstant/(electron.y - height)**2)

                # Other electrons' repulsions
                otherElectrons = self.electrons[:i] + self.electrons[i+1:]
                for otherElectron in otherElectrons:

                    dx = electron.x - otherElectron.x
                    dy = electron.y - otherElectron.y
                    magnitude = ((dx)**2 + (dy)**2)
                    theta = atan2(dy,dx)

                    if magnitude == 0:
                        magnitude = random.uniform(0,10)
                        theta = random.uniform(0,10)
                    electron.ax += electronRepulsionConstant / (magnitude) * cos(theta)
                    electron.ay += electronRepulsionConstant / (magnitude) * sin(theta)

                # Take into account links
                course = self.courses[i]
                for prereq in course.prereqs:
                    # Take into account prereq tension
                    try:
                        j = self.courses.index(Course(prereq))
                        otherElectron = self.electrons[j]
                        x1,y1 = otherElectron.getCoords()
                        dx = x1 - electron.x
                        dy = y1 - electron.y
                        magnitude = ((dx)**2 + (dy)**2) ** 0.5 - r*2
                        theta = atan2(dy,dx)
                        electron.ax += hookesLawK * (magnitude) * cos(theta)
                        electron.ay += hookesLawK * (magnitude) * sin(theta)
                        otherElectron.ax -= hookesLawK * (magnitude) * cos(theta)
                        otherElectron.ay -= hookesLawK * (magnitude) * sin(theta)
                    except:
                        pass

            for electron in self.electrons:
                electron.doPhysics()
    
    def courseExists(self, courseNumber):
        return Course(courseNumber) in self.courses

    def addCourse(self, courseNumber, status=False, courseName = "No name", prereqs = ()):
        if not self.courseExists(courseNumber):
            self.courses.append(Course(courseNumber, status, courseName, prereqs))
            #self.coordinates.append(getNextCoordinate(self.coordinates[-1]))
            self.electrons.append(Electron(cx,cy))

            if status == 1: self.completedCourses += 1
            elif status == 2: self.completedCourses += 0.5



    def drawCourses(self):
        for i in xrange(len(self.courses)):
            course = self.courses[i]
            x0,y0 = self.electrons[i].getCoords()

            # Draw arrows representing prereqs
            prereqsMissing = False
            prereqsFulfilled = True
            for prereq in course.prereqs:
                # Draw arrow from prereq
                try:
                    j = self.courses.index(Course(prereq))
                    if self.courses[j].status == 0: prereqsFulfilled = False
                    x1,y1 = self.electrons[j].getCoords()

                    theta = atan2(y1-y0,x1-x0)
                    self.canvas.create_line(x0+r*cos(theta),y0+r*sin(theta),x1-r*cos(theta),y1-r*sin(theta),arrow=FIRST)
                except:
                    prereqsMissing = True

            if course.status == 0: colour = "white"
            elif course.status == 1: colour = "green"
            elif course.status == 2: colour = "yellow"

            if prereqsMissing:
                outlineColour = "red"
            else:
                if prereqsFulfilled:
                    outlineColour = "green"
                else:
                    outlineColour = "black"


            self.canvas.create_oval(x0-r,y0-r,x0+r,y0+r,fill=colour,outline=outlineColour,width=2)
            self.canvas.create_text(x0,y0,text=course.courseNumber)
    
    def drawSpiral(self):
        for i in xrange(len(self.coordinates)-1):
            x0,y0 = self.coordinates[i]
            x1,y1 = self.coordinates[i+1]
            self.canvas.create_line(scale*x0+cx, scale*y0+cy, scale*x1+cx, scale*y1+cy)

    def drawCompletionPercentage(self):
        percentComplete = self.completedCourses*100.0/len(self.courses)
        self.canvas.create_text(width+100,100,text="%d%%"%percentComplete,fill="white",font="Arial 80 bold")

    def drawControls(self):
        self.canvas.create_rectangle(width,0,width+controlsWidth,height,fill="black")
        self.drawCompletionPercentage()

    def redrawAll(self):
        self.canvas.delete(ALL)
        # draw the text
        self.drawCourses()
        self.drawControls()

        #self.drawSpiral()
    

    def onMouseReleasedWrapper(self, event):
        self.shapeSelected = False

        if self.pressCoordinates == (event.x, event.y):
            global testCourseNumber

            if testCourseNumber == 1:
                self.addCourse("21-127", 1)
            elif testCourseNumber == 2:
                self.addCourse("15-122", 2, "", ("15-112","21-127"))
            elif testCourseNumber == 3:
                self.addCourse("76-101", 1)
            elif testCourseNumber == 4:
                self.addCourse("15-221", 0, "", ("76-101",))
            elif testCourseNumber == 5:
                self.addCourse("15-251", 2, "", ("15-112",))
            elif testCourseNumber == 6:
                self.addCourse("15-150", 0, "", ("15-112",))
            elif testCourseNumber == 7:
                self.addCourse("15-213", 0, "", ("15-122",))
            elif testCourseNumber == 8:
                self.addCourse("15-210", 0, "", ("15-122","15-150"))
            elif testCourseNumber == 9:
                #self.addCourse("21-241", 1)
                pass
            elif testCourseNumber == 10:
                self.addCourse("15-451", 0, "", ("21-241", "15-210", "15-251"))
            elif testCourseNumber == 11:
                self.addCourse("21-120", 1, "", ())
            elif testCourseNumber == 12:
                self.addCourse("21-122", 1, "", ("21-120",))
            elif testCourseNumber == 13:
                self.addCourse("21-259", 2, "", ("21-122",))
            elif testCourseNumber == 14:
                self.addCourse("15-462", 0, "", ("21-241", "15-213", "21-259"))
            elif testCourseNumber == 15:
                self.addCourse("16-385", 0, "", ("15-122", "21-241", "21-259"))
            elif testCourseNumber == 16:
                self.addCourse("16-311", 0, "", ("21-241",))

            #self.addCourse(str(testCourseNumber))
            testCourseNumber += 1

    def onMouseMotionWrapper(self, event):
        if self.shapeSelected:
            electron = self.electrons[self.indexOfElectronSelected]
            electron.x = event.x
            electron.y = event.y

    def initAnimation(self):
        self.root.bind("<ButtonRelease-1>", self.onMouseReleasedWrapper)
        self.root.bind("<B1-Motion>", self.onMouseMotionWrapper)

EventBasedAnimationDemo().run()
