from import_data.import_data import DataImporter
from BlackScholesCalibrator import ImpliedVolatility
import numpy as np
from BlackScholesCalibrator import ImpliedVolatility
import pandas as pd
from functools import lru_cache 


class VolatilitySurface():
    """
    Classe pour interpoller la surface de volatilité. (Voir dernière méthode destinée à l'interpolation)
    Nous avons caché les différentes méthodes de calcul de vol implicite, donc il n y aura pas un 
    temps d'atteinte si l'on modifie les paramètres(tel K,T) qui ne sont pas en entrée de la classe.
    """
    def __init__(self,  market_date, ticker ='AAPL', mode= 'Calls', r=0.045, d=0.005):
        """
        Args :
        market_date (datetime.datetime) : Date du marché.
        ticker (str) : Symbole boursier de l'action (par défaut 'AAPL').
        mode (str) : mode d'extraction de vol implicite (soit à travers des données des calls ou des puts).
        r (float) : Taux d'intérêt sans risque annuel .
        d (float) : Taux de dividende continu .
        """
        self.market_date = market_date 
        self.mode_implied_vol = mode 
        self.ticker = ticker
        self.stock_price, self.opt_data = self.input_datas(mode) 
        self.r = r 
        self.d= d
        self.type_px = self.type_px(mode)
        list_strikes = list(set(self.opt_data['strike']))
        list_strikes.sort()
        list_expiries = list(set(self.opt_data['T']))
        list_expiries.sort()
        self.list_strikes_in = list_strikes
        self.list_expiries_in = list_expiries

    def CallPutsData(self):
        data_importer = DataImporter(self.ticker, self.market_date)
        spot_price = data_importer.get_stock_price()
        calls, puts = data_importer.get_all_options_data()
        return spot_price, calls, puts 
     
        
    def input_datas(self, mode:str):
        spot_price, calls_data, puts_data = self.CallPutsData()
        if mode == 'Calls':
            return spot_price, calls_data 
        elif mode == 'Puts':
            return spot_price, puts_data
        elif mode == 'Straddle':
            df_tab_merged = calls_data.merge(puts_data, left_on=['strike', 'Expiration_Date', 'T'], 
                                             right_on=['strike', 'Expiration_Date', 'T'])[['Expiration_Date', 
                                                                                      'strike', 
                                                                                      'T',
                                                                                      'lastPrice_x', 
                                                                                      'lastPrice_y']]
            #Puts + Calls
            df_tab_merged['lastPrice'] = df_tab_merged['lastPrice_x'] + df_tab_merged['lastPrice_y']
            return spot_price, df_tab_merged
        else: 
            raise Exception('Invalid Mode')

    def type_px(self, mode):
        dict_t = {'Calls': 0, 'Puts': 1, 'Straddle': 2}
        return dict_t[mode]
    
    @lru_cache
    def DataWithImpliedVolsCalculated(self):
        opt_data = self.opt_data 
        #implied vols from calls
        implied_vols = [ImpliedVolatility(self.stock_price, K, T, self.r, self.d, target_px, self.type_px).implied_volatility()
                        for T, K, target_px in zip(list(opt_data['T']),list(opt_data['strike']), list(opt_data['lastPrice']))]
        opt_data ['implied_vols_calculated' ] = implied_vols

        return opt_data

    @lru_cache
    def VolMap(self):
        data_with_vol = self.DataWithImpliedVolsCalculated()  
        return {(K,T):vol  for K, T, vol in   zip(list(data_with_vol['strike']), list(data_with_vol['T']), list(data_with_vol['implied_vols_calculated'])) }

    @lru_cache
    def QuoteMap(self):
        data_with_vol = self.DataWithImpliedVolsCalculated()  
        return {(K,T):quote  for K, T, quote in   zip(list(data_with_vol['strike']), list(data_with_vol['T']), list(data_with_vol['lastPrice'])) }

    @lru_cache 
    def DataWithImpliedVolsCalculatedFiltered(self):
        data_with_vol = self.DataWithImpliedVolsCalculated()
        strikes_filtered = self.ListStrikesFiltered()
        return data_with_vol[data_with_vol.strike.isin(strikes_filtered)]

    @lru_cache
    def VolMapDF(self):

        list_strikes = self.ListStrikes()
        list_expiries = self.ListExpiries()
        vol_map = self.VolMap()
        list_dicts_vols =[]
        for K in list_strikes:

            dict_K = {}
            dict_K['K'] = K 
            for T in list_expiries:
                dict_K[T] = vol_map.get((K,T), np.nan)
                
            list_dicts_vols += [dict_K]

        df_vol = pd.DataFrame(list_dicts_vols)
        return df_vol 
    
    @lru_cache 
    def VolMapDfNoNan(self):
        df_vol = self.VolMapDF()
        return df_vol.dropna()

    def ListStrikes(self):
        return self.list_strikes_in
    
    def ListStrikesFiltered(self):
        return list(self.VolMapDfNoNan()['K'])
    
    def MaxMinStrikes(self):
        list_strikes = self.ListStrikesFiltered()
        return max(list_strikes), min(list_strikes)
    
    def ListExpiries(self):
        return self.list_expiries_in

    def MaxMinExpiries(self):
        list_expiries = self.ListExpiries()
        return max(list_expiries), min(list_expiries)
 
    def search_closest_two_strikes(self, K:float):
        Kmax, Kmin = self.MaxMinStrikes()
        list_strikes = self.ListStrikesFiltered()
        if K in list_strikes:
            return K, K
        if K<=Kmin: #on extrapole flat
            return Kmin, Kmin
        elif K>=Kmax: 
            return Kmax, Kmax 

        else:  
            d = K - Kmin
            count  = 0 
            while d> 0:
                count = count +1
                d = K - list_strikes[count] 
            return list_strikes[count-1], list_strikes[count]

    def search_closest_two_expiries(self, T:float):
        Tmax, Tmin = self.MaxMinExpiries()
        list_expiries = self.ListExpiries()
        if T in list_expiries:
            return T, T
        if T<Tmin: #on extrapole flat
            return Tmin, Tmin
        elif T>Tmax: 
            return Tmax, Tmax 
        else:  
            d = T - Tmin
            count  = 0 
            while d> 0:
                count = count +1
                d = T - list_expiries[count] 
            return list_expiries[count-1], list_expiries[count]

    def InterpolatedVol(self, K:float, T:float)-> float:
        """
        Interpolation linéaire de la volatilité en fonction de K et T.

        Paramètres :
        K (float) : Prix d'exercice.
        T (float) : Échéance.

        Retourne :
        float : Volatilité interpolée.
        """
        K_left, K_right = self.search_closest_two_strikes(K)
        T_up, T_down = self.search_closest_two_expiries(T)
        vol_map = self.VolMap()

        if K_left == K_right and T_down == T_up:
            return vol_map.get((K_left, T_down), np.nan)
        elif K_left == K_right:
            vd = vol_map.get((K_left, T_down), np.nan)
            vu = vol_map.get((K_left, T_up), vd)
            return (vd if np.isnan(vu) else (vu if np.isnan(vd) else (T - T_down) * vu + (T_up - T) * vd) / (T_up - T_down))
        elif T_down == T_up:
            vl = vol_map.get((K_left, T_down), np.nan)
            vr = vol_map.get((K_right, T_down), vl)
            return (vl if np.isnan(vr) else (vr if np.isnan(vl) else (K - K_left) * vr + (K_right - K) * vl) / (K_right - K_left))
        else:
            vul = vol_map.get((K_left, T_up), np.nan)
            vur = vol_map.get((K_right, T_up), vul)
            vdl = vol_map.get((K_left, T_down), np.nan)
            vdr = vol_map.get((K_right, T_down), vdl)

            if np.isnan(vul) or np.isnan(vur) or np.isnan(vdl) or np.isnan(vdr):
                return np.nan

            vu = ((K - K_left) * vur + (K_right - K) * vul) / (K_right - K_left)
            vd = ((K - K_left) * vdr + (K_right - K) * vdl) / (K_right - K_left)
            
            return ((T - T_down) * vu + (T_up - T) * vd) / (T_up - T_down)

