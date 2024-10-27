import numpy as np
from Hull_white import HullWhite


class BondPricing:
    def __init__(self, hull_white_model: HullWhite):
        self.hull_white_model = hull_white_model

    def price_zero_coupon_bond(self, T : float, short_rate_paths: np.ndarray) -> float:
        _, num_steps = short_rate_paths.shape
        dt = T / num_steps
        discount_factors = np.exp(-np.cumsum(short_rate_paths, axis=1) * dt)

        return np.mean(discount_factors[:, -1])
    
    def FRA(self, T1: float, T2 : float , short_rate_paths: np.ndarray) -> float :
        _,num_steps = short_rate_paths.shape
        delta = T1-T2
        fra= (self.price_zero_coupon_bond(T1,short_rate_paths[:,:int(T1*num_steps)])/ self.price_zero_coupon_bond(T2,short_rate_paths[:,:int(T2*num_steps)])) -1
        return fra/delta
    
    def price_fixed_leg_swap(self, N : float, K : float, T: list, short_rate_paths : np.ndarray) -> float:
        _,num_steps = short_rate_paths.shape
        pv_fix = 0 
        for j in range(1,len(T)) : 
            delta_j = (T[j]-T[j-1])
            discount_factor = self.price_zero_coupon_bond(T[j],short_rate_paths[:,:int(T[j]*num_steps)])
            pv_fix += (delta_j*discount_factor)
        return N*K*pv_fix
    
    def price_var_leg_swap(self, N : float, T : list, short_rate_paths : np.ndarray) -> float:
        _,num_steps = short_rate_paths.shape
        pv_var = 0 
        for j in range(1,len(T)) : 
            delta_j = (T[j]-T[j-1])
            discount_factor = self.price_zero_coupon_bond(T[j],short_rate_paths[:,:int(T[j]*num_steps)]) * self.FRA(T[j-1],T[j],short_rate_paths)
            pv_var += (delta_j*discount_factor)
        return N*pv_var
    
    def swap_price(self, N : float, K : float, T  : list, short_rate_paths : np.ndarray) -> float: 
        fixed_leg_price = self.price_fixed_leg_swap(N, K, T, short_rate_paths)
        var_leg_price = self.price_var_leg_swap(N,T,short_rate_paths)
        return fixed_leg_price+var_leg_price
    
    def taux_swap(self,T : list, short_rate_paths : np.ndarray) -> float:
        _,num_steps = short_rate_paths.shape
        zcb_t1 = self.price_zero_coupon_bond(T[0],short_rate_paths[:,:int(T[0]*num_steps)])
        zcb_tn = self.price_zero_coupon_bond(T[-1],short_rate_paths[:,:int(T[-1]*num_steps)])
        discount_factor = 0
        for j in range(1,len(T)) : 
            delta_j = (T[j]-T[j-1])
            discount_factor += delta_j*self.price_zero_coupon_bond(T[j],short_rate_paths[:,:int(T[j]*num_steps)]) 
        return (zcb_t1 - zcb_tn)/discount_factor