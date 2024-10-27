import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from scipy.integrate import cumtrapz

class HullWhite:
    def __init__(self,theta :float =0.1 , alpha :float = 0.5,sigma :float =0.02) -> None:
        self.theta = theta
        self.alpha = alpha
        self.sigma = sigma
    
    def sim_process(self,T,num_steps :int =252,num_paths: int =1000)-> np.ndarray :
        dt = T/num_steps
        sqrt_dt = np.sqrt(dt)
        short_rate_paths = np.zeros((num_paths, num_steps + 1))

        for i in range(num_paths):
            short_rate = 0.0
            for j in range(num_steps):
                dW = np.random.normal(0, sqrt_dt)
                d_short_rate = self.alpha * (self.alpha - short_rate) * dt
                d_short_rate += self.sigma * sqrt_dt * dW
                short_rate += d_short_rate
                short_rate_paths[i, j + 1] = short_rate

        return short_rate_paths

