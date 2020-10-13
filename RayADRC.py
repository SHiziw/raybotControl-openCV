# -*- coding: utf-8 -*-

import time
import numpy as np



class ADRC:
    def __init__(self, b1=0.2, b2=0.0, b3=0.0, k1=0.0, k2=0.0, h=0.0, b0=0.0 ):

        self.b0 = b0
        self.b1 = b1
        self.b2 = b2
        self.b3 = b3
        self.k1 = k1
        self.k2 = k2
        
        self.h = h  #sample_time
        self.current_time = time.time()
        self.last_time = self.current_time        
        self.current_time = time.time()
        self.delta_time = self.current_time - self.last_time
        self.u = 0.0   
        
        # self.TD()
        self.v0 =0.0
        self.h0 = 0.001
        self.r0 = 2000
        self.v1 =0.0
        self.v2 =0.0  
        # self.ESO()
        self.z1 = 0.0
        self.z2 = 0.0
        self.z3 = 0.0
        # self.NEFC()
        self.umax = 200
        self.umin = -200
                     
    def restart(self):
        self.z1 = 0.0
        self.z2 = 0.0
        self.z3 = 0.0
        self.v0 =0.0       
        self.v1 =0.0
        self.v2 =0.0  
        
    def sat(self, x, delta):
        return  x/delta if np.abs(x)<delta else np.sign(x)


    def fal(self, x, alpha=0.5, delta=0.1):
        return  x/np.power(delta,1-alpha) if np.abs(x)<delta else np.power(np.abs(x), alpha)*np.sign(x)
    def TD(self,feedback_value):
        
        delta=0.1    
        self.v1 += self.h*self.v2
        self.v2 += self.h*(-self.r0*self.sat((self.v1 - self.v0 + np.abs(self.v2)*self.v2/(2*self.r0)), delta))

        # self.v1=feedback_value
    def ESO(self,feedback_value):       
        self.e1 = self.z1-feedback_value
        self.z1 += self.h*(self.z2 - self.b1 * self.e1)
        self.z2 += self.h*(self.z3 - self.b2 * self.e1+self.b0*self.u)
        self.z3 += self.h*(- self.b3 * self.e1)

    def NEFC(self):
        self.r1 = self.v1-self.z1
        # self.r2 = self.v2-self.z2
        self.r2 = self.v2-self.z2
        self.u  = (self.k1*self.fal(self.r1)+self.k2*self.fal(self.r2)-self.z3)/self.b0
   
        
        if self.u>self.umax:
           self.u=self.umax
        if self.u<self.umin:
           self.u=self.umin
 
    def update(self, feedback_value):
        """Calculates PID value for given reference feedback
        .. math::
            u(t) = K_p e(t) + K_i \int_{0}^{t} e(t)dt + K_d {de}/{dt}
        .. figure:: images/pid_1.png
           :align:   center
           Test PID with Kp=1.2, Ki=1, Kd=0.001 (test_pid.py)
        """
        
        # self.ESO(feedback_value)
        # self.NEFC()
    

        self.current_time = time.time()
        delta_time = self.current_time - self.last_time

        if (delta_time >= self.h):
            self.TD(feedback_value)
            self.ESO(feedback_value)           
            self.NEFC()              
            # Remember last time and last error for next calculation
            self.last_time = self.current_time
           
            
    def setb0(self, b0):
        """Determines how aggressively the PID reacts to the current error with setting Proportional Gain"""
        self.b0 = b0

    def setb1(self, b1):
        self.b1 = b1
        
    def setb2(self, b2):
        self.b2 = b2
        
    def setb3(self, b3):
        self.b3 = b3
        
    def setk1(self, k1):
        self.k1 = k1

    def setK2(self, k2):
        """Determines how aggressively the PID reacts to the current error with setting Derivative Gain"""
        self.k2 = k2

    def setv0(self, v0):
        self.v0 = v0
       
        
    def setSampleTime(self, h):
        """Based on a pre-determined sampe time, 
        decides if it should compute or return immediately.
        """
        self.h = h     
        
        
        
        
        
        
        
        