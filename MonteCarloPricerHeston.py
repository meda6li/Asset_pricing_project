import numpy as np
from MonteCarloSimulator import MonteCarloSimulatorWithHeston

class MonteCarloPricerHeston():
    '''Pricer à vol stochastique de produits exotiques et vanilles(voir classes filles)'''
    def __init__(self, S:float, r:float, d:float, sigma:float, kappa:float, theta:float, rho:float, xi:float, T:float, numsim:int, antithetic:bool):
        self.stock_simulator = MonteCarloSimulatorWithHeston(S, r, d, sigma, kappa, theta, rho, xi, numsim)
        self.paths = self.stock_simulator.spot_paths_simulator(T, antithetic)
        self.r, self.d , self.S, self.T, self.numsim = r, d, S, T, numsim

        
    def payoff(self, single_path):
        return 
        
    def price(self, antithetic=False):   
        '''Méthode permettant de pricer les différents produits'''       
        payoff_paths = np.array([self.payoff(path) for path in self.paths])
        factor = 2. if antithetic else 1.
        return np.sum(payoff_paths) * np.exp(-self.r * self.T) / (self.numsim * factor)
    
    
class MonteCarloCallPricerHeston(MonteCarloPricerHeston):
    def __init__(self, S, K, r, d, sigma, kappa, theta, rho, xi, T, numsim, antithetic):
        super().__init__(S, r, d, sigma, kappa, theta, rho, xi, T, numsim, antithetic)
        self.K = K 
        
    def payoff(self, single_path)-> float:        
        return np.maximum(single_path[-1] - self.K, 0) 
    
    
class MonteCarloPutPricerHeston(MonteCarloPricerHeston):
    def __init__(self, S, K, r, d, sigma, kappa, theta, rho, xi, T, numsim, antithetic):
        super().__init__(S, r, d, sigma, kappa, theta, rho, xi, T, numsim, antithetic)
        self.K = K 
        
    def payoff(self, single_path)-> float:        
        return np.maximum( self.K- single_path[-1], 0)   
    
class MonteCarloAsiaticCallPricerHeston(MonteCarloPricerHeston):
    def __init__(self, S, K, r, d, sigma, kappa, theta, rho, xi, T, numsim, antithetic):
        super().__init__(S, r, d, sigma, kappa, theta, rho, xi, T, numsim, antithetic)
        self.K = K 
        
    def payoff(self, single_path)-> float:        
        return np.maximum(np.average(single_path) - self.K, 0)   
   
class MonteCarloAsiaticPutPricerHeston(MonteCarloPricerHeston):
    def __init__(self, S, K, r, d, sigma, kappa, theta, rho, xi, T, numsim, antithetic):
        super().__init__(S, r, d, sigma, kappa, theta, rho, xi, T, numsim, antithetic)
        self.K = K 
             
    def payoff(self, single_path)-> float:        
        return np.maximum(self.K - np.average(single_path) , 0)         
    
    
class MonteCarloLookBackMaxPricerHeston(MonteCarloPricerHeston):
    def __init__(self, S, K, r, d, sigma, kappa, theta, rho, xi, T, numsim, antithetic):
        super().__init__(S, r, d, sigma, kappa, theta, rho, xi, T, numsim, antithetic)
        self.K = K 
        
    def payoff(self, single_path)-> float:
        return np.maximum(np.max(single_path)- self.K, 0)   
    
class MonteCarloLookBackMinPricerHeston(MonteCarloPricerHeston):
    def __init__(self, S, K, r, d, sigma, kappa, theta, rho, xi, T, numsim, antithetic):
        super().__init__(S, r, d, sigma, kappa, theta, rho, xi, T, numsim, antithetic)
        self.K = K 
        
    def payoff(self, single_path)-> float:
        return np.maximum(np.min(single_path)- self.K, 0)