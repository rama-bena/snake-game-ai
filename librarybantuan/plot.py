import torch
import numpy as np
import matplotlib.pyplot as plt
from IPython import display
from captum.attr import IntegratedGradients


plt.ion()

def plot(scores, title, interative=True):
    # display.clear_output(wait=True)
    # display.display(plt.gcf())
    plt.clf()
    plt.title(title)
    plt.xlabel('Number of Games')
    plt.ylabel('Value')

    plt.plot(scores, label='score')
    # plt.plot(rewards, label='reward')

    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    # plt.text(len(rewards)-1, rewards[-1], str(rewards[-1]))
    
    plt.legend()

    if interative:
        plt.show(block=False)
        plt.pause(.1)
    else:
        plt.show(block=True)

def feature_importance(model, state, target, title):
        ig = IntegratedGradients(model)
        state = torch.tensor(state, dtype=torch.float)        
        state.requires_grad_()
        feature_names = list(np.arange(81)) + ['up', 'right', 'down', 'left', 'iteration']
        # target_names = ['Straight', 'Turn Right', 'Turn Left']
        x_pos = (np.arange(len(feature_names)))
    
        plt.figure(figsize=(25, 10))
        plt.title(title)
        plt.xlabel("Features")
        plt.xticks(x_pos, feature_names, wrap=True, rotation=90)        
        # for target in range(3):
        attr, delta = ig.attribute(state, target=target, return_convergence_delta=True)
        attr = attr.detach().numpy()
        importances = np.mean(attr, axis=0)
        plt.bar(x_pos, importances, align='center')
        
        plt.grid()
        plt.show()