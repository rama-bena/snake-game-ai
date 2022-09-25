import numpy as np
import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot(scores, degree=5, iterative=True):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Skor per game')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')

    x_list = np.arange(len(scores))
    plt.plot(x_list, scores)
    fit = np.polyfit(x_list, scores, degree)
    y_list = []    
    for x in x_list:
        y = np.sum([fit[i]*(x**(degree-i)) for i in range(degree+1)])
        y_list.append(y)

    plt.plot(x_list, y_list)
    
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(y_list)-1, y_list[-1], str(y_list[-1]))
    
    if iterative:
        plt.show(block=False)
        plt.pause(.1)
    else:
        plt.show()