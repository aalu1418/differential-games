import numpy as np
import math
import matplotlib.pyplot as plt
import animationScript as animate

# state parameter order:
# x[0] = x0 (pursuer x-coordinate)
# x[1] = y0 (pursuer y-coordinate)
# x[2] = theta (heading angle for pursuer measured from y-axis, radians)
# x[3] = x1 (evader x-coordinate)
# x[4] = y1 (evader y-coordinate)

# input parameters
# input[0] = phi (ratio for theta_dot, limiting turn rate for pursuer)
# input[1] = psi (heading angle for evader, measured from y-axis, radians)

# constant parameters
# const[0] = speed of pursuer
# const[1] = speed of evader
# const[2] = turn radius of pursuer
const = np.array([0.01, 0.006, 0.1]) #global parameters for this system


def dXdt(x0, input):
    #theta dot limiter
    if abs(input[0]) > 1 :
        input[0] = 1*np.sign(input[0])

    x_dot = np.empty(5)

    #note this causes a delay where theta is changed, but the direction is not changed until the next step
    # x_dot[0] = const[0]*np.sin(x0[2])
    # x_dot[1] = const[0]*np.cos(x0[2])
    # x_dot[2] = const[0]/const[2]*input[0]

    #simultaneous update of theta
    theta_dot = const[0]/const[2]*input[0]
    x_dot[0] = const[0]*np.sin(x0[2]+theta_dot)
    x_dot[1] = const[0]*np.cos(x0[2]+theta_dot)
    x_dot[2] = theta_dot

    x_dot[3] = const[1]*np.sin(input[1])
    x_dot[4] = const[1]*np.cos(input[1])
    return x0+x_dot

def phiToEvader(x):
    angle = np.pi/2-np.arctan2(x[4]-x[1], x[3]-x[0]) #calculate angle to target
    angleDiff = angle-x[2] #calculate difference between current heading and target heading
    return angleDiff/(const[0]/const[2]) #calculate the ratio of the required rate

def distance(x0, y0, x1, y1):
    return math.sqrt((x0-x1)**2+(y0-y1)**2)

def randomPsi(current, ii):
    if ii%20 == 0:
        current += np.pi*(np.random.rand()-0.5)
    return current


if __name__=='__main__':
    x0 = np.array([0, 0, 0, 1, 1]) # initial parameters

    X = np.array([x0])
    # for ii in np.arange(20):
    ii = 0;
    psi = np.pi/2
    while True:
        phi_calc = phiToEvader(X[-1])
        psi = randomPsi(psi, ii)
        input = np.array([phi_calc, psi])
        x_step = dXdt(X[-1], input)
        X = np.append(X, [x_step], axis=0)
        ii += 1

        #exit condition if pursuer catches evader
        if distance(X[-1,0], X[-1,1], X[-1,3], X[-1,4]) < 1e-2:
            print("steps:", ii)
            break
        if ii >= 10000:
            print("max steps:", ii)
            break

    # plt.figure()
    # plt.plot(X[:,0], X[:,1], 'r', X[:,3], X[:,4], 'b')
    # plt.plot(X[-1,0], X[-1,1], 'ro', X[-1,3], X[-1,4], 'bo')
    # plt.axis('equal')
    # plt.show()

    # animate.animate(X[:,0], X[:,1], X[:,3], X[:,4], "homChauffeur")
    animate.animate(X[:,0], X[:,1], X[:,3], X[:,4])
