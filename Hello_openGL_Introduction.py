from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


def draw_points(x, y):
    glPointSize(100) #pixel size. by default 1 thake
    glBegin(GL_POINTS)
    glVertex2f(x,y) #jekhane show korbe pixel
    glEnd()


def iterate():
    glViewport(0, 0, 500, 500)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 500, 0.0, 500, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    glColor3f(0.0, 1.0, 0.0) #konokichur color set (RGB)
    #call the draw methods here
    draw_points(400, 300)
    glutSwapBuffers()



glutInit()
#glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(1000, 1000) #window size
#glutInitWindowPosition(100, 50)
wind = glutCreateWindow(b"OpenGL Coding Practice") #window name
glutDisplayFunc(showScreen)

glutMainLoop()