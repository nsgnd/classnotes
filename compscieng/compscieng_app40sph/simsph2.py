# convert  -delay 20 /tmp/glut/glutout-*.png /tmp/balls2.gif
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from random import random
from PIL import Image
from PIL import ImageOps
from collections import defaultdict 
import numpy as np, datetime
import sys, numpy.linalg as lin

p1,p2,p3 = 73856093, 19349663, 83492791
#G = np.array([0.0, 0.0, -0.8])
G = np.array([0.0, 0.0, -9.8])

m = 0.1
B = 10 # top
l = 0.2 # bolec kutu buyuklugu
n = B*20 # bolec sozluk buyuklugu

GAS_CONST = 2000.
REST_DENS = 1000.
MASS = 1.0
VISC = 250.0
DT = 0.0008
H = 0.2 # kernel radius
HSQ = H*H # radius^2 for optimization
POLY6 = 315.0/(65.0*np.pi*np.power(H, 9.));
SPIKY_GRAD = -45.0/(np.pi*np.power(H, 6.));
VISC_LAP = 45.0/(np.pi*np.power(H, 6.));


img = True

def spatial_hash(x):
    """
    x = [x0,x1,x2] uc boyutlu kordinatlari icin bir bolec (hash) degeri uret
    """
    ix,iy,iz = np.floor((x[0]+2.0)/l), np.floor((x[1]+2.0)/l), np.floor((x[2]+2.0)/l)
    return (int(ix*p1) ^ int(iy*p2) ^ int(iz*p3)) % n

class Simulation:
    def __init__(self):
        self.geo_hash_list = None
        self.i = 0
        self.r   = 0.05
        self.dt  = 0.01
        #self.cor = 0.6        
        self.cor = 1.0
        self.balls = []
        self.tm  = 0.0
        self.th  = 200.0
        self.mmax =  1.0-self.r
        self.mmin = -1.0+self.r
        self.right = False
        self.left = False
        
    def init(self):
        bi = 0
        for xs in np.linspace(-0.4, 0.4, 10):
            for ys in np.linspace(-0.4, 0.4, 10):
                for zs in np.linspace(0.0, 0.2, 4):
                    v = np.array([0.0, 0.0, 0.0])
                    f = np.array([0,0,0])
                    x = np.array([xs, ys, zs])
                    d = {'x': x, 'f':f, 'v': v, 'i': bi, 'rho': 0.0, 'p': 0.0}
                    self.balls.append(d)
                    bi += 1

                        
        tm = 0.0

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glClearColor(1.0,1.0,1.0,1.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60.0,1.0,1.0,50.0)
        glTranslatef(0.0,0.0,-3.5)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def hash_balls(self):
        self.geo_hash_list = defaultdict(list)        
        for j,b in enumerate(self.balls):
            self.geo_hash_list[spatial_hash(self.balls[j]['x'])].append(self.balls[j])
          
    def computeDensityPressure(self):
        for i,bi in enumerate(self.balls):
            h = spatial_hash(self.balls[i]['x']) # su anki topun boleci
            if (len(self.geo_hash_list[h])>1): # yakinda top var mi
                otherList = self.geo_hash_list[h] # varsa isle
                bi['rho'] = 0.0                
                for j,bj in enumerate(otherList):
                    r2 = lin.norm(bi['x']-bj['x'])**2
                    if  r2 < HSQ:
                        bi['rho'] += MASS*POLY6*np.power(HSQ-r2, 3.0)
                bi['p'] = GAS_CONST*(bi['rho'] - REST_DENS)
       
                
    def computeForces(self):
        for i,bi in enumerate(self.balls):
            fpress = np.array([0.0, 0.0, 0.0])
            fvisc = np.array([0.0, 0.0, 0.0])                
            h = spatial_hash(self.balls[i]['x']) # su anki topun boleci
            if (len(self.geo_hash_list[h])>1): # yakinda top var mi
                otherList = self.geo_hash_list[h] # varsa isle
                for j,bj in enumerate(otherList):
                    if bj['i'] == bi['i']: continue
                    rij = bi['x']-bj['x']
                    r = lin.norm(rij)
                    if np.sum(rij)>0.0: rij = rij / r
                    if r < H:                        
                        tmp = (2.0 * bj['rho']) * SPIKY_GRAD*np.power(H-r,2.0)
                        fpress += -rij*MASS*(bi['p'] + bj['p']) / tmp
                fgrav = G * bi['rho']
                bi['f'] = fpress + fvisc + fgrav
                        
    def integrate(self):
        
        for j,b in enumerate(self.balls):
            b['v'] += self.dt*(b['f']/m)
            b['x'] += self.dt*b['v']
            
            if (abs(b['x'][0]) >= self.mmax):
                #print (b['i'], 'wall 1')
                b['v'][0] *= -self.cor
                if b['x'][0] < 0:
                    b['x'][0] = self.mmin

            if (abs(b['x'][1]) >= self.mmax):
                #print (b['i'], 'wall 2')
                b['v'][1] *= -self.cor
                if b['x'][1] < 0:
                    b['x'][1] = self.mmin
                    
            if (abs(b['x'][2]) >= self.mmax):
                #print (b['i'], 'wall 3')
                b['v'][2] *= -self.cor
                if b['x'][2] < 0:
                    b['x'][2] = self.mmin
        
        self.hash_balls()
                
                    
            
    def update(self):
        self.hash_balls()
        self.computeDensityPressure()
        self.computeForces()
        self.integrate()                    
        glutPostRedisplay()

    def display(self):
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(self.th,0.0,1.0,0.0)
        glRotatef(90.0,-1.0,0.0,0.0)
        glutWireCube(2.0)
        for j,b in enumerate(self.balls):
            glPushMatrix()
            glTranslatef(b['x'][0],b['x'][1],b['x'][2])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.0, 0.0, 1.0, 1.0])
            glutSolidSphere(self.r,50,50)
            glPopMatrix()
        glPopMatrix()
        glutSwapBuffers()

        if img and self.i % 10 == 0: 
            width,height = 480,480
            data = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
            image = Image.frombytes("RGBA", (width, height), data)
            image = ImageOps.flip(image)
            image.save('/tmp/glut/glutout-%03d.png' % self.i, 'PNG')
            
        self.i += 1

if __name__ == '__main__':
    if (os.path.exists("/tmp/glut") == False): os.mkdir("/tmp/glut")
    s = Simulation()
    glutInit(())    
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(500,500)
    glutCreateWindow("GLUT Bouncing Ball in Python")
    glutDisplayFunc(s.display)
    glutIdleFunc(s.update)
    s.init()
    glutMainLoop()

