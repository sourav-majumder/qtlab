from scipy.optimize import leastsq
import numpy as np
import matplotlib.pyplot as plt


def main():
   # data provided
   x=np.array([1.0,2.5,3.5,4.0,1.1,1.8,2.2,3.7])
   y=np.array([6.008,15.722,27.130,33.772,5.257,9.549,11.098,28.828])
   # here, create lambda functions for Line, Quadratic fit
   # tpl is a tuple that contains the parameters of the fit
   funcLine=lambda tpl,x : tpl[0]*x+tpl[1]
   funcQuad=lambda tpl,x : tpl[0]*x**2+tpl[1]*x+tpl[2]
   # func is going to be a placeholder for funcLine,funcQuad or whatever 
   # function we would like to fit
   func=funcLine
   # ErrorFunc is the diference between the func and the y "experimental" data
   ErrorFunc=lambda tpl,x,y: func(tpl,x)-y
   #tplInitial contains the "first guess" of the parameters 
   tplInitial1=(1.0,2.0)
   # leastsq finds the set of parameters in the tuple tpl that minimizes
   # ErrorFunc=yfit-yExperimental
   tplFinal1,success=leastsq(ErrorFunc,tplInitial1[:],args=(x,y))
   print " linear fit ",tplFinal1
   xx1=np.linspace(x.min(),x.max(),50)
   yy1=func(tplFinal1,xx1)
   #------------------------------------------------
   # now the quadratic fit
   #-------------------------------------------------
   func=funcQuad
   tplInitial2=(1.0,2.0,3.0)

   tplFinal2,success=leastsq(ErrorFunc,tplInitial2[:],args=(x,y))
   print "quadratic fit" ,tplFinal2
   xx2=xx1

   yy2=func(tplFinal2,xx2)
   plt.plot(xx1,yy1,'r-',x,y,'bo',xx2,yy2,'g-')
   plt.show()

if __name__=="__main__":
   main()
