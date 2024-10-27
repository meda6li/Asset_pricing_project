import numpy as np
import datetime
from HestonSemiClosedFormula import HestonSemiAnalyticalFormula
from VolatilitySurface import VolatilitySurface
from functools import lru_cache 
from scipy.optimize import least_squares

@lru_cache
def get_vol_surface(market_date:datetime.datetime, ticker:str, mode:str, r:float, d:float):
    return VolatilitySurface(market_date, ticker, mode, r, d)
        
class HestonCalibrator:
    """
    Classe pour calibrer les paramètres du modèles d'heston theta, rho(corrélation), kappa, xi(la vol de vol), sigma(volatilité initial)
    """
    def __init__(self, market_date:datetime.datetime, ticker:str, mode:str, r:float, d:float, calib_fast = False):
        """
        Args:
            market_date (datetime.datetime): Date du marché.
            ticker (str): Symbole boursier.
            mode (str): Mode d'extraction des paramètres de heston.
            r (float): Taux d'intérêt sans risque.
            d (float): Taux de dividende.
            calib_fast (bool, optional): Un calibrage unpeu plus rapide en enlevant certains strikes.
        """
        self.r = r
        self.d = d
        vol_surf = get_vol_surface(market_date, ticker, mode, r, d)
        self.S = vol_surf.stock_price

        quote_map = vol_surf.DataWithImpliedVolsCalculatedFiltered()

        if calib_fast == True: 
            quote_map = quote_map[(quote_map.strike>self.S - 20) & (quote_map.strike<self.S + 20)]
        self.list_strikes = quote_map['strike'].to_numpy('float')
        self.maturities = quote_map['T'].to_numpy('float')
        self.quotes = quote_map['lastPrice'].to_numpy('float')
        self.vols =quote_map['implied_vols_calculated'].to_numpy('float')
        self.type_px = self.type_px(mode)
        
    def type_px(self, mode:str)-> int:
        dict_t = {'Calls': 0, 'Puts': 1, 'Straddle': 2}
        return dict_t[mode]
    
    def CalibrationROutine(self):
        S, strikes, mats, quotes, r, d = self.S, self.list_strikes, self.maturities, self.quotes, self.r, self.d
        def objective_function(x):           
            theta, rho, kappa, xi, sigma = x[0], x[1], x[2], x[3], x[4]
            
            return quotes - HestonSemiAnalyticalFormula(S, strikes, mats, sigma, r, d, kappa, theta, rho, xi).price(self.type_px)
        
        # Résolution en utilisant la méthode de moindre carrée
        initial_values = np.array([0.5, -0.5, 0.5, 0.5, 0.5])
        lower_bounds= np.array ([1e-2, -1., 1e-2, 1e-2, 1e-2])
        upper_bounds= np.array ([10, 1., 10., 10., 10.])

        return least_squares(objective_function, initial_values, 
                                bounds=(lower_bounds, upper_bounds))
    

    def HestonParameters(self):
        theta, rho, kappa, xi, sigma = self.CalibrationROutine().x
        return theta, rho, kappa, xi, sigma
    
    
    

    
    