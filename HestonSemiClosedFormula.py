import numpy as np


i = complex(0, 1)

class HestonSemiAnalyticalFormula():
    '''Classe de calcul de formule semi fermée du modèle d'Heston pour un call et un put'''
    def __init__(self, S:float, K:float, T:float,sigma:float, r:float, d:float, kappa:float, theta:float, rho:float, xi:float):
        self.S, self.K, self.T = S, K, T 
        self.sigma, self.r, self.d = sigma, r, d
        self.kappa, self.theta, self.rho, self.xi = kappa, theta, rho, xi

    # Heston Pricer
    def priceHestonMid(self)->float:
        St, K, T, r, q = self.S, self.K, self.T, self.r, self.d
        theta, sigma, rho, kappa, volvol = self.theta, self.sigma, self.rho, self.kappa, self.xi
        def fHeston(s):
            prod = rho * sigma * i * s

            d1 = (prod - kappa)**2
            d2 = (sigma**2) * (i * s + s**2)
            d = np.sqrt(d1 + d2)

            g1 = kappa - prod - d
            g2 = kappa - prod + d
            g = g1 / g2

            exp1 = np.exp(np.log(St) * i * s) * np.exp(i * s * r * T)
            exp2 = 1 - g * np.exp(-d * T)
            exp3 = 1 - g
            mainExp1 = exp1 * np.power(exp2 / exp3, -2 * theta * kappa/              (sigma**2))

            exp4 = theta * kappa * T / (sigma**2)
            exp5 = volvol / (sigma**2)
            exp6 = (1 - np.exp(-d * T)) / (1 - g * np.exp(-d * T))
            mainExp2 = np.exp((exp4 * g1) + (exp5 * g1 * exp6))
            return (mainExp1 * mainExp2)
        
        P, iterations, maxNumber = 0, 1000, 100
        ds = maxNumber / iterations
        element1 = 0.5 * (St*np.exp(-q*T) - K * np.exp(-r * T))
        # Calculate the complex integral
        # Using j instead of i to avoid confusion
        for j in range(1, iterations):
            s1 = ds * (2 * j + 1) / 2
            s2 = s1 - i
            numerator1 = fHeston(s2)
            numerator2 = K * fHeston(s1)
            denominator = np.exp(np.log(K) * i * s1) * i * s1
            P += ds * (numerator1 - numerator2) / denominator
        element2 = P / np.pi
        return np.real((element1 + element2))
    
    def call_price(self)->float:
        return self.priceHestonMid()
    
    
    def put_price (self)->float:
        '''Pour le prix du put on utilise la parité call-put'''
        return self.call_price() - self.S + self.K*np.exp(-self.r*self.T) 

    def price(self,type_px=0)->float:
        if type_px ==0 :
            return self.call_price()
        elif type_px == 1:
            return self.put_price()
        elif type_px ==2: 
            return (self.call_price() +self.put_price())
            
        else: 
            raise Exception('Invalid option type')
        
        
    
