from HestonCalibrator import *
from HestonSemiClosedFormula import HestonSemiAnalyticalFormula
from BlackScholesCalibrator import ImpliedVolatility

class VanillaPricerWithHestonCalibrated():
    '''Pricer Heston à vol stochastique de produit vanille(calibré)'''
    def __init__(self, market_date:datetime.datetime, ticker:str, mode:str, r:float, d:float):
        self.calibrator= HestonCalibrator(market_date,ticker,mode,r,d)
        self.stock_price = self.calibrator.S
        self.r = r
        self.d = d
        self.calibratedparams=self.calibrator.HestonParameters()
        
    def CallPrice(self, K:float, T:float)-> float:
        theta, rho, kappa, xi, sigma = self.calibratedparams
        return HestonSemiAnalyticalFormula(self.stock_price,K,T,sigma,self.r,self.d,kappa,theta,rho,xi).call_price()
    
    def ImpliedVol(self, K:float, T:float)-> float:
        call_price  = self.CallPrice(K,T)
        return ImpliedVolatility(self.stock_price, K, T, self.r, self.d, call_price, 0).implied_volatility()

    def PutPrice(self, K:float, T:float)-> float:
        theta, rho, kappa, xi, sigma = self.calibratedparams
        return HestonSemiAnalyticalFormula(self.stock_price,K,T,sigma,self.r,self.d,kappa,theta,rho,xi).put_price()

    def StraddlePrice(self, K:float,T:float)-> float:
        return self.CallPrice(K,T) + self.PutPrice(K,T)
    
    def CallSpread(self, K1:float, K2:float, T:float)-> float:
        return self.CallPrice(K2,T ) - self.CallPrice(K1,T)
    
    def Butterfly(self, K1:float, K2:float, K3:float, T:float)-> float:
        return self.CallPrice(K1, T) - 2*self.CallPrice(K2, T) + self.CallPrice(K3, T)
    
    def PriceStrategy(self, strategy:str, *args)-> float:
        if strategy == "call":
            return self.CallPrice(*args)
        elif strategy == "put":
            return self.PutPrice(*args)
        elif strategy == "straddle":
            return self.StraddlePrice(*args)
        elif strategy == "callSpread":
            return self.CallSpread(*args)
        elif strategy == "butterfly":
            return self.Butterfly(*args)
        else:
            raise ValueError("Unknown strategy")

        
        
            
            
            
        
            
            
        
        
        
        
        
    
    
