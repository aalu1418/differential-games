import matplotlib.pyplot as plt
from matplotlib import animation
from numpy import random

# https://stackoverflow.com/questions/23049762/matplotlib-multiple-animate-multiple-lines

def animate(x0_data, y0_data, x1_data, y1_data, savename = ""):
    fig = plt.figure()
    # ax = plt.axes(xlim=(-108, -104), ylim=(31,34))
    ax = plt.axes()
    plt.xticks([])
    plt.yticks([])
    plt.axis('equal')


    plotcols = ["red","blue"]
    plotcols_line = ["lightcoral", "cornflowerblue"]
    lines = []
    for index in range(2):
        lobj = ax.plot([],[],color=plotcols_line[index])[0]
        lines.append(lobj)

        lobj = ax.plot([],[],'o', color=plotcols[index])[0]
        lines.append(lobj)


    def init():
        for line in lines:
            line.set_data([],[])
        return lines

    x1,y1 = [],[]
    x2,y2 = [],[]

    def animate(i):
        x1.append(x0_data[i])
        y1.append(y0_data[i])

        x2.append(x1_data[i])
        y2.append(y1_data[i])

        xlist = [x1, x2]
        ylist = [y1, y2]

        for lnum in range(2):
            lines[2*lnum].set_data(xlist[lnum], ylist[lnum]) # set data for each line separately.
            lines[2*lnum+1].set_data(xlist[lnum][-1], ylist[lnum][-1])

        ax.relim()                      # reset intern limits of the current axes
        ax.autoscale_view()   # reset axes limits
        return lines

    # call the animator.  blit=True means only re-draw the parts that have changed.
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=len(x0_data), interval=25, blit=True, repeat=False)
    if savename != "":
        print("generating gif output - currently not working")
        return
        anim.save(savename+'.gif', writer='imagemagick', fps=60)
        print("output complete: "+savename+".gif")
    else:
        plt.show()


if __name__=='__main__':
    # fake data
    animate(random.rand(100), random.rand(100), random.rand(100), random.rand(100));
