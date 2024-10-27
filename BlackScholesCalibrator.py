import numpy as np

from scipy.optimize import brentq
from BlackScholesModelClosedFormula import BlackScholesModelClosedFormula

class ImpliedVolatility():
    """
    Classe de calibration pour calculer la volatilité implicite des options en utilisant le modèle de Black-Scholes.
    """
    def __init__(self, S:float, K:float, T:float, r:float, d:float, Px:float, type_px:int):
        """
        Paramètres :
        S (float) : Prix actuel de l'actif sous-jacent.
        K (float) : Prix d'exercice de l'option.
        T (float) : Temps jusqu'à l'expiration de l'option (en années).
        r (float) : Taux d'intérêt sans risque annuel.
        d (float) : Taux de dividende continu.
        Px (float) : Prix observé ou cible de l'option sur le marché.
        type_px (int) : Type de l'option (0 pour call, 1 pour put).
        """
        self.S, self.K, self.T, self.r, self.d, self.target_price, self.type_px = S, K, T, r, d, Px, type_px
  

    def implied_volatility(self) -> float:    
        """
        Calcule la volatilité implicite de l'option en utilisant la méthode de Brent.

        Retourne :
        float : Volatilité implicite calculée.

        Si la volatilité implicite ne peut pas être calculée, retourne np.nan.
        """    
        def objective_funtion(sigma):
            """
            Fonction objectif pour le calcul de la volatilité implicite.

            Paramètres :
            sigma (float) : Volatilité à évaluer.

            Retourne :
            float : Différence entre le prix calculé par Black-Scholes et le prix cible.
            """
            return BlackScholesModelClosedFormula(self.S, self.K, self.T, sigma, self.r, self.d).price(type_px = self.type_px) - self.target_price
        try:
            return brentq(objective_funtion, 0.0001, 2.0, xtol = 1e-6)
        except:
            return np.nan