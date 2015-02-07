# Todo
# Handle or for prereqs
# Undo add or remove with Cmd-U
# Save course structure
# Clicking context menu bug
# Animations for spawning and destroying courses
# Animate tooltip spawning

import random, tkSimpleDialog, tkMessageBox, os
from Tkinter import *
from math import *
from eventBasedAnimationClass import EventBasedAnimationClass
from mongoengine import *

connect("grff", host="104.47.138.204", port=3306)

# Graphics contants
width = 800
controlsWidth = 200
height = 600
cx,cy = width/2, height/2
contextMenuItemHeight = 20
r = 25

# Physics constants
repulsionConstant = 1000000.0
electronRepulsionConstant = 200000.0
hookesLawK = 0.1

# Obsolete stuff
scale = 1
testCourseNumber = 1


tooltipDelay = 1000

currentDir = os.path.dirname(__file__)

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




class Coarse(object):
    def __init__(self, courseNumber, status=0, courseName="", prereqs = (), units = 9):
        # Takes in strings courseNumber, courseName and list of courses prereqs
        # Should prereqs be a tuple of strings of course numbers
        self.courseNumber = courseNumber
        self.courseName = courseName
        self.prereqs = prereqs
        self.status = status # 0 = not taken, 1 = taken, 2 = taking
        self.units = units

    def __str__(self):
        return "%05d: %s" % (self.courseNumber, self.courseName)

    def __eq__(self, other):
        return self.courseNumber == other.courseNumber

    def getPrereqsAsString(self):
        return ", ".join(self.prereqs)

    def getBlurb(self):
        return "%s\n%s\n\nPrerequisites: %s" % (self.courseNumber, self.courseName, self.getPrereqsAsString())


courseToPrereqs = {}

courseToCourseName = {}

coursedepts = {}

for coursename in courseToPrereqs.keys():
    dept = coursename[:2]
    if dept not in coursedepts.keys():
        coursedepts[dept] = set([coursename])
    else:
        coursedepts[dept].add(coursename)




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

        self.electrons = []
        self.courses = []
        self.completedCourses = 0
        self.loadCourses()

        self.countUnits()
        self.countCompletedCourses()

        self.shapeSelected = False

        self.activesidecourse = None
        self.sideCoursesIds = []

        self.contextMenuItems = []

        self.timeHovered = 0
        self.showTooltip = False
        self.mousePressed = False

        self.mouseMotionPosition = (0,0)

    def loadCourses(self):
        try:
            with open(currentDir + os.sep + "courses.txt") as fin:
                string = fin.read()
            courses = eval(string)
            for course in courses:
                self.addCourse(*course)
        except Exception as inst:
            print inst
            self.courses = [Coarse("15-112", 1, "Fundamentals of Programming and Computer Science", (), 12)]
            self.electrons = [Electron(cx,cy)]
            self.saveCourses()

    def populatePrerequisites(self, course):
        global courseToCourseName, courseToPrereqs
        courseObj = Course.objects(code=course)
        print courseObj.count()
        try:
            course = Course.objects(code=course)[0]
        except:
            tkMessageBox.showinfo("404", "404: Course not found.")
            return -1

        if course.code in courseToCourseName: return 1

        courseToCourseName[course.code] = course.title
        

        if course.code not in courseToPrereqs:  
            courseToPrereqs[course.code] = []

        for dep in course.prerequisites:
            try:
                depCourse = Course.objects(code=dep)[0]
            except:
                tkMessageBox.showinfo("405", "405: Dependency not found.")
                continue

            if depCourse.code != course.code:
                courseToPrereqs[course.code] += [depCourse.code]
                self.populatePrerequisites(depCourse.code)
                self.addCourse(dep)

        
        self.addCourse(course.code)
        return 1
        




    def addCourseButtonPressed(self):
        courseToAdd = tkSimpleDialog.askstring("Add course", "Please enter a course number")
        if courseToAdd != None:
            # Need to handle if course not in courseToPrereqs
            if self.populatePrerequisites(int(courseToAdd))>0:
                pass
            else:
                tkMessageBox.showwarning("Coarse not found", "Coarse not found!")        
    
    def addRandomCourse(self):
        maxTries = 50
        while maxTries > 0:
            randomCourse = random.choice(courseToPrereqs.keys())
            if Coarse(randomCourse) not in self.courses: break
            maxTries -= 1
        
        if maxTries == 0: print "No more courses to add!"
        self.addCourse(randomCourse)

    def contextMenuClicked(self,x,y):
        x,yPos = self.contextMenuPosition
        option = self.contextMenuItems[(y-yPos)/contextMenuItemHeight]

        if option == "Remove course":
            self.removeCourse()
        elif option == "Add missing prerequisites":
            self.addMissingPrerequisites()

    def addMissingPrerequisites(self):
        course = self.courses[self.indexOfElectronSelected]
        missingPrereqs = []
        for prereq in course.prereqs:
            try:
                j = self.courses.index(Coarse(prereq))
            except:
                self.addCourse(prereq)

    def onKeyPressed(self, event):
        if event.keysym == "space": self.addRandomCourse()
        elif event.char == "s": self.shakeItUp()

    def onMousePressed(self, event):
        self.mousePressed = True
        self.pressCoordinates = (event.x, event.y)
        shapesSelected = self.canvas.find_withtag(CURRENT)

        if len(shapesSelected) > 0: # A shape was clicked
            if shapesSelected[0] == self.addCourseButtonId:
                self.addCourseButtonPressed()
            elif shapesSelected[0] == self.addRandomCourseButtonId:
                self.addRandomCourse()

            elif event.x < width: # A shape in main area was clicked on
                
                if len(self.contextMenuItems) > 0: # Context menu exists
                    self.contextMenuClicked(event.x, event.y)
                else: # No context menu, course must have been clicked
                    if "course" in self.canvas.gettags(shapesSelected[0]):
                        x0,y0,x1,y1 = self.canvas.coords(shapesSelected[0])
                        self.indexOfElectronSelected = self.electrons.index(Electron((x0+x1)/2,(y0+y1)/2))
                        self.shapeSelected = True
                    else:
                        # Shake it up button clicked
                        self.shakeItUp()


        self.contextMenuItems = []

    def shakeItUp(self):
        for electron in self.electrons:
            # Give random vx and vy to electron
            minV, maxV = -50, 50
            electron.vx = random.uniform(minV, maxV)
            electron.vy = random.uniform(minV, maxV)

    def removeCourse(self):
        self.courses.pop(self.indexOfElectronSelected)
        self.electrons.pop(self.indexOfElectronSelected)
        
        self.countCompletedCourses()
        self.countUnits()

        self.saveCourses()

    def saveCourses(self):
        filePath = currentDir + os.sep + "courses.txt"
        with open(filePath, "wt") as fout:
            fout.write("[")
            for i in xrange(len(self.courses)):
                course = self.courses[i]
                fout.write(str((course.courseNumber, course.status)))
                if i < len(self.courses)-1:
                    fout.write(",")
            fout.write("]")


    def countCompletedCourses(self):
        count = 0
        for course in self.courses:
            if course.status == 1: count += 1
            elif course.status == 2: count += 0.5
        self.completedCourses = count

    def courseIsHovered(self):
        x,y = self.mouseMotionPosition
        for electron in self.electrons:
            if ((x-electron.x)**2 + (y-electron.y)**2) ** 0.5 < r: return True
        return False

    def onTimerFired(self):

        # Sense hovers
        pointerPositionNow = self.root.winfo_pointerxy()
        if not self.mousePressed and pointerPositionNow == self.pointerPositionPrev:
            self.timeHovered += self.timerDelay
        else: self.timeHovered = 0

        if self.timeHovered > tooltipDelay and self.courseIsHovered() and len(self.contextMenuItems) == 0: self.showTooltip = True
        else: self.showTooltip = False
        self.pointerPositionPrev = pointerPositionNow

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
                        j = self.courses.index(Coarse(prereq))
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
        return Coarse(courseNumber) in self.courses

    def addCourse(self, courseNumber, status=0):
        if not self.courseExists(courseNumber):
            prereqs = courseToPrereqs[courseNumber]
            try:
                courseName = courseToCourseName[courseNumber]
            except:
                courseName = "NaN"
            self.courses.append(Coarse(courseNumber, status, courseName, prereqs))
            #self.coordinates.append(getNextCoordinate(self.coordinates[-1]))
            self.electrons.append(Electron(cx,cy))

            if status == 1: self.completedCourses += 1
            elif status == 2: self.completedCourses += 0.5

            self.countUnits()
            self.saveCourses()

    def drawSideCourses(self):
        
        fx = width + controlsWidth/2
        fy = height/2

        for buttonno in xrange(13): #1-10 displays, 11 for prevoius, 12 for next, 13 for back
            newfy = 30*buttonno+fy
            x0 = fx-90
            x1 = fx+90
            y0 = fy-15
            y1 = fy+15            
            self.canvas.create_rectangle(x0,y0,x1,y1,fill="red", activefill="yellow", outline=None, tags="course")
            

        if self.activesidecourse == None: #case where theres no active menu
            for coursedeptname in sorted(coursedepts.keys()):
        #        newbutton = self.canvas.create_rectangle(x0,y0,x1,y1,fill="red", activefill="yellow", outline=None, tags="course")
                #self.sideCoursesIds.append(newbutton)
                self.canvas.create_text(fx,fy, text=coursedeptname)
            for revbuttonno in xrange(13,10,-1):
                newfy = 30*buttonno+fy
                if revbuttonno ==13: self.canvas.create_text(fx, newfy+15, text="Back")
                if revbuttonno ==13: self.canvas.create_text(fx, newfy+15, text="Back")
                if revbuttonno ==13: self.canvas.create_text(fx, newfy+15, text="Back")


        
        else: # case where there is an active menu
            self.sideCoursesIds = []
            for coursename in sorted(courseToPrereqs.keys()):
                if coursename.startswith(str(self.activesidecourse)):
                    x0 = fx-90
                    x1 = fx+90
                    y0 = fy-15
                    y1 = fy+15
                    newbutton = self.canvas.create_rectangle(x0,y0,x1,y1,fill="red", activefill="yellow", outline=None)
                    self.sideCoursesIds.append(newbutton)
                    self.canvas.create_text(fx,fy, text=coursename)
                    fy+=30
            self.canvas.create_rectangle(x0,y0,x1,y1,fill="green", activefill="yellow", outline=None)
            self.canvas.create_text(fx,fy, text="back")

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
                    j = self.courses.index(Coarse(prereq))
                    if self.courses[j].status == 0: prereqsFulfilled = False
                    x1,y1 = self.electrons[j].getCoords()

                    theta = atan2(y1-y0,x1-x0)
                    self.canvas.create_line(x0+r*cos(theta),y0+r*sin(theta),x1-r*cos(theta),y1-r*sin(theta),arrow=FIRST)
                except:
                    prereqsMissing = True

            if course.status == 0:
                colour = "white"
                activefillcolour = "grey"
            elif course.status == 1:
                colour = "green"
                activefillcolour = "#00D000"
            elif course.status == 2:
                colour = "yellow"
                activefillcolour = "#D0D000"

            if prereqsMissing:
                outlineColour = "red"
            else:
                if prereqsFulfilled:
                    outlineColour = "green"
                else:
                    outlineColour = "black"


            self.canvas.create_oval(x0-r,y0-r,x0+r,y0+r,fill=colour,outline=outlineColour,width=2,activefill=activefillcolour,tags="course")
            self.canvas.create_text(x0,y0,text=course.courseNumber,font="Arial 13 bold",state=DISABLED)
    
    def drawSpiral(self):
        for i in xrange(len(self.coordinates)-1):
            x0,y0 = self.coordinates[i]
            x1,y1 = self.coordinates[i+1]
            self.canvas.create_line(scale*x0+cx, scale*y0+cy, scale*x1+cx, scale*y1+cy)

    def drawCompletionPercentage(self):
        percentComplete = 0 if self.completedCourses == 0 else self.completedCourses*100.0/len(self.courses)
        self.canvas.create_text(width+controlsWidth/2,controlsWidth/4,text="%d%%"%percentComplete,fill="white",font="Arial 80 bold")

        encouragement = ""
        if percentComplete == 100:
            encouragement = "Congratulations! You have completed college!"
        elif 75 <= percentComplete < 100:
            encouragement = "Way to go! Almost there!"
        elif 60 <= percentComplete < 75:
            encouragement = "You're about two-thirds done now"
        elif 50 <= percentComplete < 60:
            encouragement = "Woah! Halfway done! Good job!"
        elif 10 <= percentComplete < 30:
            encouragement = "So far, so good"
        elif 0 <= percentComplete < 10:
            encouragement = "So you wanna be startin' something..."
        self.canvas.create_text(width+controlsWidth/2,controlsWidth/1.5,text=encouragement,fill="white",width=controlsWidth,justify=CENTER)


    def drawAddCourseButton(self):
        buttonPadding = 10
        buttonHeight = 30
        x0,y0 = width+buttonPadding, controlsWidth+buttonPadding
        x1,y1 = width+controlsWidth-buttonPadding, y0 + buttonHeight

        self.addCourseButtonId = self.canvas.create_rectangle(x0,y0,x1,y1,fill="grey",activefill="light grey")
        cx,cy = (x0+x1)/2, (y0+y1)/2
        self.canvas.create_text(cx,cy,text="Add course by number",state=DISABLED)

    def drawAddRandomCourseButton(self):
        buttonPadding = 10
        buttonHeight = 30
        x0,y0 = width+buttonPadding, controlsWidth+2*buttonPadding+buttonHeight
        x1,y1 = width+controlsWidth-buttonPadding, y0 + buttonHeight

        self.addRandomCourseButtonId = self.canvas.create_rectangle(x0,y0,x1,y1,fill="grey",activefill="light grey")
        cx,cy = (x0+x1)/2, (y0+y1)/2
        self.canvas.create_text(cx,cy,text="Add random course",state=DISABLED)

    def drawControls(self):
        self.canvas.create_rectangle(width,0,width+controlsWidth,height,fill="black")
        self.drawCompletionPercentage()
        self.drawAddCourseButton()
        self.drawAddRandomCourseButton()
        #self.drawSideCourses()

    def drawContextMenu(self):
        contextMenuWidth = 150
        contextMenuHeight = contextMenuItemHeight * len(self.contextMenuItems)
        x,y = self.contextMenuPosition

        padding = 5
        for i in xrange(len(self.contextMenuItems)):
            cx,cy = padding, (i + 0.5) * contextMenuItemHeight
            self.canvas.create_rectangle(x,y+contextMenuItemHeight*i,x+contextMenuWidth,y+contextMenuItemHeight*(i+1),fill="light yellow",activefill="navy blue")
            self.canvas.create_text(x+cx,y+cy,text=self.contextMenuItems[i],font="Arial 12 bold",state=DISABLED,anchor=W)

    def drawTooltip(self):
        tooltipWidth = 150
        tooltipHeight = 100
        x,y = self.mouseMotionPosition
        self.canvas.create_rectangle(x,y,x+tooltipWidth,y+tooltipHeight,fill="light yellow",state=DISABLED,width=0)

        for i in xrange(len(self.electrons)):
            electron = self.electrons[i]
            if ((x-electron.x)**2 + (y-electron.y)**2) ** 0.5 < r: break
        course = self.courses[i]
        tooltipPadding = 5
        self.canvas.create_text(x+tooltipPadding,y+tooltipPadding,text=course.getBlurb(), anchor=NW, font="Arial 11", width = tooltipWidth-2*tooltipPadding)

    def countUnits(self):
        unitsTaken = 0
        unitsTotal = 0
        for course in self.courses:
            courseUnits = course.units
            unitsTotal += courseUnits
            if course.status > 0: unitsTaken += courseUnits
        self.unitsTaken = unitsTaken
        self.unitsTotal = unitsTotal

    def drawUnitCount(self):
        padding = 10
        x,y = width-padding, height-padding
        self.canvas.create_text(x,y,text="Unit Count: %d/%d" % (self.unitsTaken, self.unitsTotal),anchor=SE)

    def drawShakeItUpButton(self):
        margin = 20
        buttonHeight = 30
        buttonWidth = 100
        x0 = margin*2
        x1 = margin+buttonWidth
        y1 = height-margin
        y0 = y1-buttonHeight
        self.canvas.create_rectangle(x0,y0,x1,y1,fill="grey", activefill="light grey")
        cx,cy = (x0+x1)/2, (y0+y1)/2
        self.canvas.create_text(cx,cy,text="Shake It Up!")

    def redrawAll(self):
        self.canvas.delete(ALL)

        self.drawCourses()
        self.drawUnitCount()
        self.drawShakeItUpButton()

        self.drawControls()

        if len(self.contextMenuItems) > 0:
            self.drawContextMenu()


        if self.showTooltip: self.drawTooltip()
    
    def courseClicked(self):
        shapesSelected = self.canvas.find_withtag(CURRENT)
        if len(shapesSelected) > 0:
            # Check that tag of item is "course"
            if "course" in self.canvas.gettags(shapesSelected[0]): return True
        return False

    def changeCourseStatus(self):
        # Toggles status of course at self.indexOfElectronSelected
        course = self.courses[self.indexOfElectronSelected]
        course.status += 1
        course.status %= 3

        self.countCompletedCourses()
        self.countUnits()
        self.saveCourses()

    def onMouseReleasedWrapper(self, event):
        self.mousePressed = False
        self.shapeSelected = False

        if self.pressCoordinates == (event.x, event.y) and event.x < width:
            # White area clicked!
            if self.courseClicked():
                self.changeCourseStatus()
            '''
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
                self.addCourse("21-241", 1)
            elif testCourseNumber == 10:
                self.addCourse("15-451", 0, "", ("21-241", "15-210", "15-251"))
            elif testCourseNumber == 11:
                self.addCourse("21-120", 1)
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
            '''

    def onMouseMovedWrapper(self, event):
        if self.shapeSelected:
            electron = self.electrons[self.indexOfElectronSelected]
            electron.x = event.x
            electron.y = event.y

    def hasMissingPrerequisites(self, course):
        for prereq in course.prereqs:
            try:
                j = self.courses.index(Coarse(prereq))
            except:
                return True
        return False



    def onRightMousePressed(self, event):
        self.contextMenuItems = []
        shapesSelected = self.canvas.find_withtag(CURRENT)
        if event.x < width and len(shapesSelected) > 0: # Right clicked on one of the shapes in the display area
            x0,y0,x1,y1 = self.canvas.coords(shapesSelected[0])
            self.indexOfElectronSelected = self.electrons.index(Electron((x0+x1)/2,(y0+y1)/2))

            # Populating context menu
            if self.hasMissingPrerequisites(self.courses[self.indexOfElectronSelected]):
                self.contextMenuItems.append("Add missing prerequisites")
            self.contextMenuItems.append("Remove course")

            self.contextMenuPosition = (event.x, event.y)

    def onMouseMotion(self, event):
        self.mouseMotionPosition = (event.x, event.y)
        self.timeHovered = 0

    def onDoubleClick(self, event):
        shapesSelected = self.canvas.find_withtag(CURRENT)
        if event.x < width and len(shapesSelected) > 0: # Right clicked on one of the shapes in the display area
            if "course" in self.canvas.gettags(shapesSelected[0]):
                x0,y0,x1,y1 = self.canvas.coords(shapesSelected[0])
                self.indexOfElectronSelected = self.electrons.index(Electron((x0+x1)/2,(y0+y1)/2))
                self.addMissingPrerequisites()


    def initAnimation(self):
        self.root.bind("<ButtonRelease-1>", self.onMouseReleasedWrapper)
        self.root.bind("<B1-Motion>", self.onMouseMovedWrapper)

        if os.name=="nt": # windows
            rightclick = "<Button-3>"
        elif os.name == "posix": #mac
            rightclick="<Button-2>"
        self.root.bind(rightclick, self.onRightMousePressed)
        self.root.bind("<Motion>", self.onMouseMotion)
        self.root.bind("<Double-Button-1>", self.onDoubleClick)

        self.root.title("See your future")

        self.pointerPositionPrev = self.root.winfo_pointerxy()



EventBasedAnimationDemo().run()
