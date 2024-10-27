# Guide d'utilisateur

L'application comprend les 6 premiers onglets, chacun offrant des fonctionnalités spécifiques pour l'évaluation des produits dérivés.

1. **Black-Scholes Vol. Constante** : Utilisation du modèle Black-Scholes avec une volatilité constante.
2. **Monte Carlo - BS Vol. Constante** : Évaluation par méthode Monte Carlo sous l'hypothèse de la volatilité constante du modèle Black-Scholes.
3. **Black-Scholes avec Smile de Volatilité** : Version améliorée du modèle Black-Scholes intégrant le smile de volatilité.
4. **Heston Calibrée** : Utilisation du modèle de Heston avec des paramètres calibrés.
5. **Monte Carlo Heston** : Évaluation par méthode Monte Carlo en utilisant le modèle de Heston.

## Précisions

Pour les onglets **Black-Scholes avec Smile de Volatilité**,**Black-Scholes Vol. Constante** et **Heston Calibrée** vous pouvez choisir de valoriser 5 types de stratégies : call, put, straddle, call spread, butterfly. De plus, deux modes d'extraction des paramètres calibrés sont disponibles : soit à partir des données des calls, soit des puts.

Pour les onglets **Monte Carlo - BS Vol. Constante** et **Monte Carlo Heston**, vous avez la possibilité de pricer 2 produits vanilles (par exemple, call/put européen) et 4 produits exotiques (call/put asiatique, LookBack min/max).


## Remarques Générales

- Il est impératif de recliquer sur les différents boutons relatifs aux calculs après chaque changement d'input (par exemple, calcul de prix, calcul de grecques, affichage de surface de volatilité).

## Remarques Spécifiques

### Black-Scholes avec Smile de Volatilité
- Temps d'attente pour le calcul : environ 6 secondes.
- Une fois le calcul réalisé, il n'y aura plus de temps d'attente si vous gardez les mêmes taux 'r' et 'd', car les méthodes relatives à ces paramètres sont cachées.

### Heston Calibrée
- Temps d'attente pour le calcul : entre 1 et 2 minutes.
- Comme pour le Black-Scholes avec Smile de Volatilité, une fois le calcul réalisé, il n'y aura plus de temps d'attente pour les mêmes raisons.

### Monte Carlo Heston
- Pour cette partie, nous avons choisi de ne pas inclure la calibration des paramètres afin de réduire les temps de calcul. Nous recommandons donc aux utilisateurs de prendre les paramètres déjà calibrés dans l'onglet Heston Calibrée ainsi que le prix du sous-jacent. Cela permettra à l'utilisateur de réaliser le pricing des produits exotiques dont le sous-jacent est un certain stock.

