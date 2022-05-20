import torch
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from IPython import display
from captum.attr import IntegratedGradients

degrees = [2, 5, 10, 20, 50]

def make_smooth_line(scores, degree):
    setengah = int((len(scores)/degree)//2 + 1)
    rata_rata = []
    for i in range(0, len(scores)):
        dari = max(i-setengah, 0)
        sampai = min(i+setengah+1, len(scores))
        data = scores[dari:sampai]
        rata_rata.append(sum(data)/len(data))
    return rata_rata

def plot(scores, title, interative=True):
    plt.ion()
    plt.clf()
    plt.title(title)
    plt.xlabel('Number of Games')
    plt.ylabel('Score')

    plt.plot(scores, label='score')
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    
    # if len(scores) > 10*degrees[0]:
    #     degrees.pop(0)
    # rata_rata = make_smooth_line(scores, max(len(scores)//5, 2))
    # plt.plot(rata_rata, label='rata-rata')
    # plt.text(len(rata_rata)-1, rata_rata[-1], str(rata_rata[-1]))

    plt.legend()

    if interative:
        plt.show(block=False)
        plt.pause(.1)
    else:
        plt.show(block=True)

def feature_importance(visual_range, model, state, x_pos, target, label):
        ig = IntegratedGradients(model)
        state = torch.tensor(state, dtype=torch.float)        
        state.requires_grad_()
             
        # for target in range(3):
        attr, delta = ig.attribute(state, target=target, return_convergence_delta=True)
        attr = attr.detach().numpy()
        importances = np.mean(attr, axis=0)
        plt.bar(x_pos, importances, align='center', label=label)
        
        plt.grid()