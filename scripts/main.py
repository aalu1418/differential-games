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

#phi calculation using single state
def phiSingleState(X):
    #only use most recent state
    if len(X) < 1:
        x = X[0]
    else:
        x = X[-1]

    angle = np.arctan2(x[4]-x[1], x[3]-x[0]) #calculate angle to target
    # print("wrapped:  ", angle)
    angleDiff = (np.pi/2-angle)-x[2] #calculate difference between current heading and target heading
    return angleDiff/(const[0]/const[2]) #calculate the ratio of the required rate

#more robust phi calculation using angle history + unwrapping
def phiThetaHistory(X):
    if len(X) > 1:
        angles = np.arctan2(X[:,4]-X[:,1], X[:,3]-X[:,0]) #calculate all angles to target
        angle = np.unwrap(angles)[-1] #use unwrap to create a continuous array and get last element
        # print("unwrapped:", angle, " wrapped:  ", angles[-1])
        angleDiff = (np.pi/2-angle)-X[-1, 2] #calculate the angle difference
        return angleDiff/(const[0]/const[2]) #calculate the required phi
    else:
        return phiSingleState(X) #return required phi for first calculation

# distance formula
def distance(x0, y0, x1, y1):
    return math.sqrt((x0-x1)**2+(y0-y1)**2)

#generate random psi direction
def psiRandom(psi, ii, X):
    if ii%20 == 0: #every 20 steps generate a random psi
        psi += np.pi*(np.random.rand()-0.5)
    return psi

#avoid pursuer by turning 90 degrees from pursuer
def psiTurn90(psi, ii, X):
    #only use most recent state
    if len(X) < 1:
        x = X[0]
    else:
        x = X[-1]

    if ii%5 == 0: #every 5 steps calculate a new psi
        # print(np.pi/2 - np.arctan2(x[4]-x[1], x[3]-x[0]), x[2])
        theta = x[2]%(2*np.pi) #calculate the current pursuer theta (mod 2pi for consistency)
        pursuerHeading = np.pi/2 - np.arctan2(x[4]-x[1], x[3]-x[0]) # calculate the angle from pursuer to target
        turnDirection = np.sign(pursuerHeading - theta) #get the sign of the difference to determine which direction to move
        psi = pursuerHeading + np.pi/2*turnDirection #calculate new psi of evader
    return psi

#run simulation using specied phi function and psi function
def runSim(x0, phiFunc, psiFunc, randomPsi=True, output=True):
    X = np.array([x0])

    ii = 0;
    psi = np.pi*2*np.random.rand() if randomPsi else np.pi/2 #random psi depending on condition
    while True:
        phi = phiFunc(X) #calculate phi
        psi = psiFunc(psi, ii, X) #calculate psi
        input = np.array([phi, psi])
        x_step = dXdt(X[-1], input) #input into step
        X = np.append(X, [x_step], axis=0)
        ii += 1

        #exit condition if pursuer catches evader
        if distance(X[-1,0], X[-1,1], X[-1,3], X[-1,4]) < 1e-2:
            if output:
                print("Winner: Pursuer - steps:", ii)
            break
        #exit condition if too many steps (equivalent of running out of gas)
        if ii >= 10000:
            if output:
                print("Winner: Evader - max steps:", ii)
            break
    return X

def runAllSim(x0):
    phiFuncs = [phiSingleState, phiThetaHistory]
    psiFuncs = [psiRandom, psiTurn90]

    for phiFunc in phiFuncs:
        for psiFunc in psiFuncs:
            X = runSim(x0, phiFunc, psiFunc, randomPsi=True, output=False)
            if len(X) < 10000:
                winner = "Pursuer - "+str(len(X))+" steps"
            else:
                winner = "Evader"
            print(phiFunc.__name__, "vs", psiFunc.__name__,":", winner)

if __name__=='__main__':
    # np.random.seed(1000)
    x0 = np.array([0, 0, 0, 1, 1]) # initial parameters
    # runAllSim(x0) #enable to run all simulations in comparison mode

    X = runSim(x0, phiThetaHistory, psiTurn90)
    # X = runSim(x0, phiThetaHistory, psiTurn90, randomPsi=False)

    # # plot non-animated figure
    # plt.figure()
    # plt.plot(X[:,0], X[:,1], 'r', X[:,3], X[:,4], 'b')
    # plt.plot(X[-1,0], X[-1,1], 'ro', X[-1,3], X[-1,4], 'bo')
    # plt.axis('equal')
    # plt.show()

    # animate.animate(X[:,0], X[:,1], X[:,3], X[:,4], "homChauffeur") #for rendering to .gif file (currently not working)
    animate.animate(X[:,0], X[:,1], X[:,3], X[:,4]) #display animated figure
