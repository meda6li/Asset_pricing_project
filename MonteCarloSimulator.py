import numpy as np

class MonteCarloSimulatorWithConstantVol():
    '''Simulateur des trajectoirs de prix à partir de la solution de l'EDS du modèle BS'''
    def __init__(self, S:float, r:float, d:float, sigma:float,  numsim:int):
        self.S = S        
        self.r = r
        self.d = d        
        self.sigma = sigma  
        # self.T = T        
        self.numsim = numsim  

    def simulate_brownian(self, T:float):
        
        nsteps = int(252 *T)
        delta_T = 1 / 252.
        random_normals = np.array([ np.random.randn() * np.sqrt(delta_T) for _ in range(nsteps)])
        list_t = [i*delta_T for i in range(nsteps)]
          
        return (list_t, np.cumsum(random_normals))

    def simulate_brownian_dict(self, T:float):
        t_vect, Wt_vect, = self.simulate_brownian(T)
        return dict([(t,Wt) for t, Wt in zip(t_vect, Wt_vect)])

    def spot_paths_simulator(self, T:float, antithetic=False):
        W_T_Paths = np.array([self.simulate_brownian(T)[1] for _ in range(self.numsim)])
        paths = self.S * np.exp((self.r -self.d - 0.5 * self.sigma**2) * T + self.sigma * W_T_Paths)
        if antithetic:
            paths_anti = self.S * np.exp((self.r - self.d - 0.5 * self.sigma**2) * T -  self.sigma * W_T_Paths)
            return np.array((list(paths_anti) + list(paths)))
        else:
            return paths
    

class MonteCarloSimulatorWithHeston():
    '''Simulateur des trajectoires de prix et de volatilité du modèle Heston'''
    def __init__(self, S:float, r:float, d:float, sigma:float, kappa:float, theta:float, rho:float, xi:float, numsim:int):
        self.S = S        
        self.r = r
        self.d = d        
        self.sigma = sigma  #v_0 volatilité initiale
        self.kappa = kappa
        self.theta = theta
        self.rho = rho
        self.xi = xi

        self.numsim = numsim     
        
 
    def spot_paths_simulator(self, T, antithetic=False):
        dt = 1/252.
        steps = int(252. *T)
        S_0, r, d, theta, v_0, rho, kappa, xi = self.S, self.r, self.d, self.theta, self.sigma, self.rho, self.kappa, self.xi
        Npaths, steps, dt = self.numsim, int(252. *T), 1/252.
        size = (Npaths, steps)
        prices = np.zeros(size)
        sigs = np.zeros(size)

        S_t, v_t = S_0, v_0
        for t in range(steps):
            WT = np.random.multivariate_normal(np.array([0,0]), 
                                            cov = np.array([[1,rho],
                                                            [rho,1]]), 
                                            size=Npaths) * np.sqrt(dt) 
            
            S_t = S_t*(np.exp( (r - d -0.5*v_t)*dt+ np.sqrt(v_t) *WT[:,0] ) ) 
            v_t = np.abs(v_t + kappa*(theta-v_t)*dt + xi*np.sqrt(v_t)*WT[:,1])
            prices[:, t] = S_t
            sigs[:, t] = v_t
            #to be done
            # if antithetic:
            #     S_t = S_t*(np.exp( (r - d -0.5*v_t)*dt+ np.sqrt(v_t) *WT[:,0] ) ) 
            #     v_t = np.abs(v_t + kappa*(theta-v_t)*dt + xi*np.sqrt(v_t)*WT[:,1])
            #     prices[:, t] = S_t
            #     sigs[:, t] = v_t          
              
        return prices       
    