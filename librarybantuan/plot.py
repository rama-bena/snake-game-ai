import numpy as np
import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot(scores, degree=5, iterative=True):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')

    rata_rata = []
    for i in range(0, len(scores)):
        data = scores[i:i+degree]
        rata_rata.append(sum(data)/len(data))
    

    plt.plot(scores)
    plt.plot(rata_rata)
    
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(rata_rata)-1, rata_rata[-1], str(rata_rata[-1]))
    
    if iterative:
        plt.show(block=False)
        plt.pause(.1)
    else:
        plt.show()