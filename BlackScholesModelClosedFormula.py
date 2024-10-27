from scipy.stats import norm
import numpy as np

from scipy.stats import norm

class BlackScholesModelClosedFormula():
    """
    Classe représentant le modèle de Black-Scholes pour l'évaluation des options européennes.
    """
    def __init__(self, S:float, K:float, T:float,sigma:float, r:float, d:float):
        """
        Initialise les paramètres du modèle de Black-Scholes.

        Paramètres:
        S (float) : Prix actuel de l'actif sous-jacent.
        K (float) : Prix d'exercice de l'option.
        T (float) : Temps jusqu'à l'expiration de l'option (en années).
        sigma (float) : Volatilité de l'actif sous-jacent.
        r (float) : Taux d'intérêt sans risque annuel.
        d (float) : Taux de dividende continu.
        """
        self.S = S 
        self.K = K 
        self.T = T 
        self.sigma = sigma 
        self.r = r
        self.d = d

        self.d1 = (np.log(self.S / self.K) + (self.r-self.d + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * np.sqrt(self.T))

        self.d2 = self.d1 - self.sigma * np.sqrt(self.T)
    
    def call_price(self)-> float:
        """
        Calcule le prix d'une option d'achat (call) en utilisant la formule de Black-Scholes.

        Retourne:
        float : Prix de l'option d'achat.
        """
        V = (self.S * np.exp(-self.d*self.T) * norm.cdf(self.d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(self.d2))
        return np.nan_to_num(V,nan=0.0)

    
    def put_price (self)-> float:
        """
        Calcule le prix d'une option de vente (put) en utilisant la formule de Black-Scholes.

        Retourne:
        float : Prix de l'option de vente.
        """
        V =   (self.K * np.exp(-self.r * self.T) * norm.cdf(-self.d2) - self.S * np.exp(-self.d*self.T) * norm.cdf(-self.d1))
        return np.nan_to_num(V,nan=0.0)


    def price(self,type_px=0)-> float:
        """
        Calcule le prix de l'option en fonction du type spécifié.

        Paramètres:
        type_px (int) : Type de prix à calculer. 0 pour call, 1 pour put, 2 pour le straddle.

        Retourne:
        float : Prix calculé de l'option.

        Lève:
        Exception si le type est invalide.
        """
        if type_px ==0 :
            return self.call_price()
        elif type_px == 1:
            return self.put_price()
        elif type_px ==2: 
            return (self.call_price() +self.put_price())
            
        else: 
            raise Exception('Invalid option type')
        
    #Calcul des différents Greeks avec la formule fermé de BS
    def delta(self, option_type="call")-> float:
        if option_type == "call":
            return np.exp(-self.d * self.T) * norm.cdf(self.d1)
        elif option_type == "put":
            return -np.exp(-self.d * self.T) * norm.cdf(-self.d1)

    def gamma(self,option_type="call")-> float:
        return np.exp(-self.d * self.T) * norm.pdf(self.d1) / (self.S * self.sigma * np.sqrt(self.T))

    def vega(self,option_type="call")-> float:
        return self.S * np.exp(-self.d * self.T) * norm.pdf(self.d1) * np.sqrt(self.T)

    def theta(self, option_type="call")-> float:
        if option_type == "call":
            first_term = - (self.S * norm.pdf(self.d1) * self.sigma * np.exp(-self.d * self.T)) / (2 * np.sqrt(self.T))
            second_term = self.d * self.S * norm.cdf(self.d1) * np.exp(-self.d * self.T)
            third_term = self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(self.d2)
            return first_term - second_term - third_term
        elif option_type == "put":
            first_term = - (self.S * norm.pdf(self.d1) * self.sigma * np.exp(-self.d * self.T)) / (2 * np.sqrt(self.T))
            second_term = -self.d * self.S * norm.cdf(-self.d1) * np.exp(-self.d * self.T)
            third_term = self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(-self.d2)
            return first_term + second_term + third_term

    def rho(self, option_type="call")-> float:
        if option_type == "call":
            return self.T * self.K * np.exp(-self.r * self.T) * norm.cdf(self.d2)
        elif option_type == "put":
            return -self.T * self.K * np.exp(-self.r * self.T) * norm.cdf(-self.d2)
    
            

        
        
    
    
    
