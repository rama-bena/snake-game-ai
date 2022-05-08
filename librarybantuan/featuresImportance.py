import matplotlib.pyplot as plt
from captum.attr import IntegratedGradients

def plot_fi(state, model):
    ig = IntegratedGradients(model)
    

