from cProfile import label
import torch
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from IPython import display
from captum.attr import IntegratedGradients

degrees = [2, 5, 10, 20, 50]


def plot(scores, title, interative=True):
    plt.ion()
    plt.clf()
    plt.title(title)
    plt.xlabel('Number of Games')
    plt.ylabel('Score')

    plt.plot(scores, label='score')
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))

    degree = 3
    x_list = np.arange(len(scores))
    fit = np.polyfit(x_list, scores, degree)
    y_list = []    
    for x in x_list:
        y = np.sum([fit[i]*(x**(degree-i)) for i in range(degree+1)])
        y_list.append(y)

    plt.plot(x_list, y_list, label='score rate')

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
             
        attr, delta = ig.attribute(state, target=target, return_convergence_delta=True)
        attr = attr.detach().numpy()
        importances = np.mean(attr, axis=0)
        plt.bar(x_pos, importances, align='center', label=label)
        
        plt.grid()