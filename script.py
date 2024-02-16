import numpy as np
data=np.load("data.npy");

def describeData(data):
    return [np.average(data),np.std(data),np.max(data),np.min(data)];

describeData(data);