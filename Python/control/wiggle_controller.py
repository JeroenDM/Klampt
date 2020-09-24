from controller import ControllerAccessor,ControllerBase
import math

class WiggleController(ControllerBase):
    """A controller that wiggles each of the robot's joints between their
    extrema"""
    def __init__(self,robot,period=2):
        self.robot = robot
        self.qmin,self.qmax = robot.getJointLimits()
        self.q = robot.getConfig()
        self.index = 0
        self.startTime = None
        self.period = period

    def inputNames(self):
        return ['t']

    def outputNames(self):
        return ['qcmd']

    def getState(self):
        return {'index':self.index,'startTime',self.startTime}

    def setState(self,state):
        self.index=state['index']
        self.startTime=state['startTime']
        
    def output(self,**inputs):
        api = ControllerAccessor(inputs)
        t = api.time()
        if self.startTime == None:
            self.startTime = t
        u = (t - self.startTime)/self.period
        #pick a good index
        while self.qmin[self.index]==self.qmax[self.index]:
            self.index += 1
            if self.index >= self.robot.numLinks():
                self.index = 0
        
        qdes = self.q[:]
        #wiggle between joint extrema
        if u < 0.25:
            s = math.sin(u*4*math.pi*0.5)
            qdes[self.index] += s*(self.qmax[self.index]-qdes[self.index])
            pass
        elif u < 0.75:
            s = (-math.sin(u*4*math.pi*0.5)+1.0)*0.5
            qdes[self.index] = self.qmax[self.index]+s*(self.qmin[self.index]-self.qmax[self.index])
        elif u < 1.0:
            s = math.sin(u*4*math.pi*0.5)+1.0
            qdes[self.index] = self.qmin[self.index]+s*(qdes[self.index]-self.qmin[self.index])
        else:
            #go to next index
            self.startTime = t
            self.index += 1
            if self.index >= self.robot.numLinks():
                self.index = 0
        return api.makePositionCommand(qdes)

    def signal(self,type,**inputs):
        if type=='reset':
            self.index = 0
            self.startTime = None


def make(robot):
    return WiggleController(robot)
