import numpy as np
import matplotlib.pyplot as plt
from IPython import display


def make_smooth_line(scores, degree):
    setengah = int((len(scores)/degree)//2 + 1)
    rata_rata = []
    for i in range(0, len(scores)):
        dari = max(i-setengah, 0)
        sampai = min(i+setengah+1, len(scores))
        data = scores[dari:sampai]
        rata_rata.append(sum(data)/len(data))
    return rata_rata



def plot(scores, degree=2, iterative=True):
    plt.ion()
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.figure(1)
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')


    plt.plot(scores, label='score')
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))

    degree = [2, 5, 10, 20, 50]
    for i in degree:
        rata_rata = make_smooth_line(scores, i)
        plt.plot(rata_rata, label='degree ' + str(i))
        plt.text(len(rata_rata)-1, rata_rata[-1], str(rata_rata[-1]))
    
    plt.legend()
    plt.ylim(ymin=0)
    
    if iterative:
        plt.show(block=False)
        plt.pause(.1)
    else:
        plt.show()
