import numpy as np
from MonteCarloSimulator import MonteCarloSimulatorWithConstantVol

class MonteCarloPricerWithConstantVol():
    '''Pricer à vol constante de produits exotiques et vanilles (voir classes filles)'''
    def __init__(self, S:float, r:float, d:float, sigma:float, T:float, numsim:int, antithetic:bool):
        self.stock_simulator = MonteCarloSimulatorWithConstantVol(S, r, d, sigma, numsim)
        self.paths = self.stock_simulator.spot_paths_simulator(T, antithetic)
        self.r, self.d, self.S, self.T, self.numsim = r, d, S, T, numsim
        self.antithetic = antithetic
        
    def payoff(self, single_path):
        return 
        
    def price_paths(self, paths):        
        payoff_paths = np.array([self.payoff(path) for path in paths])
        factor = 2. if self.antithetic else 1.
        return np.sum(payoff_paths) * np.exp(-self.r * self.T) / (self.numsim * factor)

    def price(self): 
        '''Méthode permettant de pricer les différents produits'''       
        return self.price_paths(self.paths)

    
class MonteCarloCallPricerBS(MonteCarloPricerWithConstantVol):
    '''Classe pour le calcul du payoff d'un call'''
    def __init__(self, S:float, r:float, d:float, sigma:float, T:float, K:float, numsim:int, antithetic:bool):
        super().__init__(S, r, d, sigma, T, numsim, antithetic)
        self.K = K 
        
    def payoff(self, single_path)-> float:      
        return np.maximum(single_path[-1] - self.K, 0) 
    
    
class MonteCarloPutPricerBS(MonteCarloPricerWithConstantVol):
    '''Classe pour le calcul du payoff d'un put'''
    def __init__(self, S:float, r:float, d:float, sigma:float, T:float, K:float, numsim:int, antithetic:bool):
        super().__init__(S, r, d, sigma, T, numsim, antithetic)
        self.K = K 
        
    def payoff(self, single_path)-> float:        
        return np.maximum(self.K- single_path[-1], 0)   
 
#Path-dependent   
class MonteCarloAsiaticCallPricerBS(MonteCarloPricerWithConstantVol):
    '''Classe pour le calcul du payoff d'un call asiatique, remarquant que le payoff depend de tout le path'''
    def __init__(self, S:float, r:float, d:float, sigma:float, T:float, K:float, numsim:int, antithetic:bool):
        super().__init__(S, r, d, sigma, T, numsim, antithetic)
        self.K = K 
        
    def payoff(self, single_path)-> float:        
        return np.maximum(np.average(single_path) - self.K, 0)   
    
    
class MonteCarloAsiaticPutPricerBS(MonteCarloPricerWithConstantVol):
    '''Classe pour le calcul du payoff d'un put asiatique, remarquant que le payoff depend de tout le path'''
    def __init__(self, S:float, r:float, d:float, sigma:float, T:float, K:float, numsim:int, antithetic:bool):
        super().__init__(S, r, d, sigma, T, numsim, antithetic)
        self.K = K 
        
    def payoff(self, single_path)-> float:
        return np.maximum(self.K - np.average(single_path) , 0)     
        
class MonteCarloLookBackMaxPricerBS(MonteCarloPricerWithConstantVol):
    '''Classe pour le calcul du payoff lookback max, remarquant que le payoff depend de tout le path'''
    def __init__(self, S:float, r:float, d:float, sigma:float, T:float, K:float, numsim:int, antithetic:bool):
        super().__init__(S, r, d, sigma, T, numsim, antithetic)
        self.K = K 
        
    def payoff(self, single_path)-> float:
        return np.maximum(np.max(single_path)- self.K, 0)   
    
class MonteCarloLookBackMinPricerBS(MonteCarloPricerWithConstantVol):
    '''Classe pour le calcul du payoff d'un lookback min, remarquant que le payoff depend de tout le path'''
    def __init__(self, S:float, r:float, d:float, sigma:float, T:float, K:float, numsim:int, antithetic:bool):
        super().__init__(S, r, d, sigma, T, numsim, antithetic)
        self.K = K 
        
    def payoff(self, single_path)-> float:
        return np.maximum(np.min(single_path)- self.K, 0)      