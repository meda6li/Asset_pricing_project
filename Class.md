classDiagram
  direction TB

  class Strategie{
    +initialiser()
    +executer() PerformanceMetrics
    +exporter_resultats()
    -univers: Univers
    -modele_facteur: ModeleFacteur
    -modele_risque: ModeleRisque
    -generateurs: List~Signal~
    -allocateur: Allocateur
    -backtester: Backtester
  }

  class DataProvider{
    -sources: string
    -frequence: string
    +charger_prix() DataFrame
    +calculer_rendements() DataFrame
  }

  class Univers{
    -actifs: List~Actif~
    +ajouter_actif(a:Actif)
    +filtrer(...)
    +iterator() Iterable~Actif~
  }

  class Actif{
    -nom: string
    -classe: string
    -rendements: Serie
    -residus: Serie
    -X: Serie
    +neutraliser_facteurs(mf:ModeleFacteur) Serie
    +integrer_residus(k:int) Serie
  }

  class ModeleFacteur{
    <<abstract>>
    -facteurs: List~Facteur~
    -methode: string
    +ajuster(fenetre:int)
    +betas(a:Actif) vec
    +residu(a:Actif,t:int) float
  }

  class ModeleACP{
    -fenetre:int
    -pcs: List~Facteur~
    +extraire_facteurs(R:DataFrame)
    +portefeuilles_propres()
  }

  class RegresseurLasso{
    -lambda: float
    +ajuster(X,y)
    +coefficients() vec
    +selection_betas()
  }

  class Facteur{
    -id:int
    -charges: Map~Actif,float~
    -serie: Serie
    +rendement(t:int) float
  }

  class ModeleRisque{
    -cov_long: Matrix
    -cov_court: Matrix
    -estimateur: string
    +estimer_cov(R:DataFrame) Matrix
    +vol(w:vec) float
    +cible_vol(R:DataFrame,sigma_target:float)
  }

  class ModeleResiduel{
    -serie: Serie
    -kappa: float
    -m: float
    -sigma: float
    -sigma_eq: float
    +ajuster_AR1(L:int)
    +estimer_OU()
    +zscore(t:int) float
    +ER_deltaX(t:int) float
  }

  class Signal{
    <<abstract>>
    +generer(a:Actif) Serie
  }

  class SignalDislocation{
    -seuil: float
    +generer(a:Actif, resid:ModeleResiduel) Serie
  }

  class SignalMomentum{
    -fenetres: Set~int~
    +generer(a:Actif) Serie
  }

  class SignalCompose{
    -regles: string
    +combiner(S1:Serie,S2:Serie) Serie
  }

  class Contraintes{
    -neutralite: bool
    -vol_cible: float
    +imposer_betas(w:vec,beta:Matrix)=0
    +bornes(w:vec)
  }

  class Allocateur{
    <<abstract>>
    +construire(signaux:Map~Actif,Serie~, cons:Contraintes, risque:ModeleRisque) vec
  }

  class AllocVolTarget{
    -sigma_target: float
    +construire(signaux,cons,risque) vec
  }

  class OptimiseurResidus{
    -a_i: vec
    -b_i: vec
    -X_t: vec
    +maximiser_ER(signaux,cons,risque) vec
  }

  class Portefeuille{
    -positions: Map~Actif,float~
    -cible_vol: float
    -valeur: Serie
    +rebalancer(w:vec)
    +PnL(t:int) float
    +backtest() PerformanceMetrics
  }

  class Backtester{
    -calendrier: Dates
    -couts: Model
    +executer(strat:Strategie) PerformanceMetrics
    +exporter_series()
  }

  class PerformanceMetrics{
    -ann_return: float
    -volatility: float
    -sharpe: float
    -max_drawdown: float
    +resume()
    +tableau()
  }

  %% Relations principales
  DataProvider --> Univers : alimente
  Univers "1" o-- "N" Actif : contient

  Strategie --> Univers
  Strategie --> ModeleFacteur
  Strategie --> ModeleRisque
  Strategie --> Signal : utilise
  Strategie --> Allocateur
  Strategie --> Backtester

  ModeleACP ..|> ModeleFacteur
  RegresseurLasso ..> ModeleFacteur : sélection betas
  ModeleFacteur --> Facteur : produit
  ModeleFacteur --> Actif : betas / résidus

  Actif --> ModeleResiduel : résidus intégrés

  SignalDislocation ..|> Signal
  SignalMomentum ..|> Signal
  SignalCompose ..|> Signal
  SignalDislocation --> ModeleResiduel : z-score
  SignalCompose --> SignalDislocation : combine
  SignalCompose --> SignalMomentum : combine

  AllocVolTarget ..|> Allocateur
  OptimiseurResidus ..|> Allocateur

  AllocVolTarget --> Contraintes
  OptimiseurResidus --> Contraintes
  AllocVolTarget --> ModeleRisque
  OptimiseurResidus --> ModeleRisque

  AllocVolTarget --> Portefeuille : w
  OptimiseurResidus --> Portefeuille : w
  Backtester --> Portefeuille : simule
  Portefeuille --> PerformanceMetrics : calcule
