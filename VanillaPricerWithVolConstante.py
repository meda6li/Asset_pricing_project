from BlackScholesModelClosedFormula import BlackScholesModelClosedFormula

class VanillaPricerWithConstanteVol():
    '''Pricer BS à vol constante de produit vanille'''
    def __init__(self, sigma=0.2,  r=0.045, d=0.005, S = None):
        self.stock_price = S
        self.r=r
        self.d=d
        self.sigma = sigma
        
    def CallPrice(self, K:float, T:float)-> float:
        return BlackScholesModelClosedFormula(self.stock_price,K,T,self.sigma,self.r,self.d).call_price()

    def PutPrice(self, K:float, T:float)-> float:
        return BlackScholesModelClosedFormula(self.stock_price,K,T,self.sigma,self.r,self.d).put_price()

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
    
    def CalculateGreek(self, greek:str, K:float, T:float, option_type="call")-> float:
        bs_greeks = BlackScholesModelClosedFormula(self.stock_price, K, T, self.sigma, self.r, self.d)
        return getattr(bs_greeks, greek)(option_type)

    def GreekForStrategy(self, strategy:str, greek:str, *args)-> float:
        if strategy == "call" or strategy == "put":
            return self.CalculateGreek(greek, *args, option_type=strategy)
        elif strategy == "straddle":
            return (self.CalculateGreek(greek, args[0], args[1], "call") +
                    self.CalculateGreek(greek, args[0], args[1], "put"))
        elif strategy == "callSpread":
            return (self.CalculateGreek(greek, args[1], args[2], "call") -
                    self.CalculateGreek(greek, args[0], args[2], "call"))
        elif strategy == "butterfly":
            return (self.CalculateGreek(greek, args[0], args[3], "call") -
                    2 * self.CalculateGreek(greek, args[1], args[3], "call") +
                    self.CalculateGreek(greek, args[2], args[3], "call"))
        else:
            raise ValueError("Unknown strategy")

        
        
            
            
            
        
            
            
        
        
        
        
        
    
    
