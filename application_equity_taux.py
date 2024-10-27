import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import numpy as np
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from VanillaPricerWithInterpolatedSmile import VanillaPricerWithsmiles
from VanillaPricerWithVolConstante import VanillaPricerWithConstanteVol
import datetime
from pandas.tseries.offsets import BDay
from functools import lru_cache 
from MonteCarloPricerBS import *
from HestonCalibrator import HestonCalibrator
from MonteCarloPricerHeston import *
from import_data import *
from VanillaPricerWithHeston import *
from Bondpricing import *
from Hull_white import *
from dash import dash_table
import pandas as pd

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Fonction pour créer une carte d'entrée
def card_input(label, id, value):
    return dbc.Card(
        dbc.CardBody([
            html.H5(label, className='card-title'),
            dcc.Input(id=id, type='number', value=value, className='form-control')
        ]),
        className='mb-3'
    )
    
def read_readme():
    with open("README.md", "r", encoding="utf-8") as file:
        return file.read()

# Mise en page pour le modèle Black-Scholes à Volatilité Constante
def layout_black_scholes_vol_constante():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H1("Modèle Black-Scholes à Volatilité Constante", className='text-center mb-4'), width=12)),
        dbc.Row([
            dbc.Col(card_input('S (Prix de l\'actif sous-jacent)', 'S-input', 100), width=4),
            dbc.Col(card_input('K (Prix d\'exercice de l\'option)', 'K-input', 100), width=4),
            dbc.Col(card_input('T (Maturité)', 'T-input', 1), width=2)
        ]),
        dbc.Row([
            dbc.Col(card_input('K2 (Second Strike Price)', 'K2-input', 110), width=4, style={'display': 'none'}, id='K2-container'),
            dbc.Col(card_input('K3 (Third Strike Price)', 'K3-input', 115), width=4, style={'display': 'none'}, id='K3-container')
        ]),
        dbc.Row([
            dbc.Col(card_input('Sigma (Volatilité)', 'sigma-input', 0.2), width=4),
            dbc.Col(card_input('r (Taux sans risque)', 'r-input', 0.05), width=4),
            dbc.Col(card_input('d (Dividende)', 'd-input', 0), width=4)
        ]),
        dbc.Row([
            dbc.Col([
                html.H5("Choisir le type de stratégie:", className='mb-2'),
                dcc.Dropdown(
                    id='option-type-dropdown',
                    options=[
                        {'label': 'Call', 'value': 'call'},
                        {'label': 'Put', 'value': 'put'},
                        {'label': 'Straddle', 'value': 'straddle'},
                        {'label': 'Call Spread', 'value': 'callSpread'},
                        {'label': 'Butterfly', 'value': 'butterfly'}
                    ],
                    value='call',
                    className='mb-3'
                )
            ], width=4)
        ]),
        dbc.Row([
            dbc.Col(html.Button('Calculer', id='calculate-button-bs', className='btn-primary btn-lg'), width={"size": 2, "offset": 5})
        ]),
        dbc.Row([
            dbc.Col(html.Button('Calculer les Grecques', id='calculate-greeks-button', className='btn-secondary btn-lg'), width=2)
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='results-output-bs'), width=2)
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='greeks-output'), width=2)
        ])
        
    ], fluid=True)

def layout_black_scholes_vol_smile():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H1("Modèle Black-Scholes avec Smile de Volatilité", className='text-center mb-4'), width=12)),
        dbc.Row([
            dbc.Col([html.H5("Symbole boursier:", className='mb-2'),
                dcc.Input(id='stock-ticker-input', type='text', value='AAPL', placeholder="Entrez un Ticker", className='mb-3')
            ], width=4),
            dbc.Col(card_input('K (Prix d\'exercice de l\'option)', 'K-input-smile', 180), width=4),
            dbc.Col(card_input('T (Maturité)', 'T-input-smile', 1), width=4)
        ]),
        dbc.Row([
            dbc.Col(card_input('K2 (Second Strike Price)', 'K2-input-smile', 110), width=4, style={'display': 'none'}, id='K2-container'),
            dbc.Col(card_input('K3 (Third Strike Price)', 'K3-input-smile', 115), width=4, style={'display': 'none'}, id='K3-container')
        ]),
        
        dbc.Row([
            dbc.Col(card_input('r (Taux sans risque)', 'r-input-smile', 0.05), width=4),
            dbc.Col(card_input('d (Dividende)', 'd-input-smile', 0), width=4)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H5("Choisir le type de stratégie:", className='mb-2'),
                dcc.Dropdown(
                    id='option-type-dropdown',
                    options=[
                        {'label': 'Call', 'value': 'call'},
                        {'label': 'Put', 'value': 'put'},
                        {'label': 'Straddle', 'value': 'straddle'},
                        {'label': 'Call Spread', 'value': 'callSpread'},
                        {'label': 'Butterfly', 'value': 'butterfly'}
                    ],
                    value='call',
                    className='mb-3'
                )
            ], width=4)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H5("Choisir le mode d'extraction de volatilité:", className='mb-2'),
                dcc.Dropdown(
                    id='mode',
                    options=[
                        {'label': 'Call', 'value': 'Calls'},
                        {'label': 'Put', 'value': 'Puts'}
                    ],
                    value='Calls',
                    className='mb-3'
                )
            ], width=4)
        ]),
        dbc.Row([
    dbc.Col(html.Button('Calculer', id='calculate-button-smile', className='btn-primary btn-lg'), width={"size": 2, "offset": 5})
    ]),
    dbc.Row([
        dbc.Col(dcc.Loading(html.Div(id='results-output-smile')), width=12)
    ]),

    dbc.Row([dbc.Col(html.Button('Afficher la Surface de Volatilité', id='show-vol-surface-button', className='btn-secondary btn-lg'), width=4)]),
    dbc.Row([
        dbc.Col(dcc.Loading(dcc.Graph(id='volatility-surface', style={'display': 'none'})), width=12)
    ]),

    dbc.Row([dbc.Col(html.Button('Calculer les Grecques', id='calculate-greeks-button', className='btn-secondary btn-lg'), width=4)]),
    dbc.Row([
        dbc.Col(dcc.Loading(html.Div(id='greeks-output-smile')), width=12)
    ])      
    ], fluid=True)
    
def layout_monte_carlo_bs_vol_constante():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H1("Monte Carlo - Black-Scholes Volatilité Constante", className='text-center mb-4'), width=12)),
        dbc.Row([
            dbc.Col(card_input('S (Prix de l\'actif sous-jacent)', 'S-input-mc', 100), width=4),
            dbc.Col(card_input('K (Prix d\'exercice de l\'option)', 'K-input-mc', 180), width=4),
            dbc.Col(card_input('T (Maturité)', 'T-input-mc', 1), width=4)
        ]),
        dbc.Row([
            dbc.Col(card_input('Sigma (Volatilité)', 'sigma-input-mc', 0.2), width=4),
            dbc.Col(card_input('r (Taux sans risque)', 'r-input-mc', 0.05), width=4),
            dbc.Col(card_input('d (Dividende)', 'd-input-mc', 0), width=4),
            dbc.Col(card_input('Nombre de Simulations', 'num-simulations', 10000), width=4)
        ]),
        dbc.Row([
            dbc.Col([
                html.H5("Choisir le type d'option exotique:", className='mb-2'),
                dcc.Dropdown(
                    id='exotic-option-type-dropdown',
                    options=[
                        {'label': 'Call Européen', 'value': 'europeanCall'},
                        {'label': 'Put Européen', 'value': 'europeanPut'},
                        {'label': 'Call Asiatique', 'value': 'asiaticCall'},
                        {'label': 'Put Asiatique', 'value': 'asiaticPut'},
                        {'label': 'LookBack Max', 'value': 'lookBackMax'},
                        {'label': 'LookBack Min', 'value': 'lookBackMin'}
                    ],
                    value='europeanCall',
                    className='mb-3'
                )
            ], width=4)
        ]),
        dbc.Row([
            dbc.Col(html.Button('Calculer Prix avec Monte Carlo', id='calculate-mc-button', className='btn-primary btn-lg'), width={"size": 2, "offset": 5})
        ]),
        
        dbc.Row([
            dbc.Col(dcc.Loading(html.Div(id='monte-carlo-result')), width=12)
        ])
    ], fluid=True)
    
    
def layout_heston_calibre():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H1(" Modèle Heston", className='text-center mb-4'), width=12)),
        dbc.Row([
            dbc.Col([html.H5("Symbole boursier:", className='mb-2'),
                dcc.Input(id='stock-ticker-input-hes', type='text', value='AAPL', placeholder="Entrez un Ticker", className='mb-3')
            ], width=4),
            dbc.Col(card_input('K (Prix d\'exercice de l\'option)', 'K-input-heston', 180), width=4),
            dbc.Col(card_input('T (Maturité)', 'T-input-heston', 1), width=4)
        ]),
        
        dbc.Row([
            dbc.Col(card_input('K2 (Second Strike Price)', 'K2-input-smile-hes', 110), width=4, style={'display': 'none'}, id='K2-container'),
            dbc.Col(card_input('K3 (Third Strike Price)', 'K3-input-smile-hes', 115), width=4, style={'display': 'none'}, id='K3-container')
        ]),
        dbc.Row([
            dbc.Col(card_input('r (Taux sans risque)', 'r-input-heston', 0.05), width=3),
            dbc.Col(card_input('d (Dividende)', 'd-input-heston', 0), width=3)
            
        ]),   
    
        
        dbc.Row([
            dbc.Col([
                html.H5("Choisir le type de stratégie:", className='mb-2'),
                dcc.Dropdown(
                    id='option-type-dropdown',
                    options=[
                        {'label': 'Call', 'value': 'call'},
                        {'label': 'Put', 'value': 'put'},
                        {'label': 'Straddle', 'value': 'straddle'},
                        {'label': 'Call Spread', 'value': 'callSpread'},
                        {'label': 'Butterfly', 'value': 'butterfly'}
                    ],
                    value='call',
                    className='mb-3'
                )
            ], width=4)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H5("Choisir le mode d'extraction des paramètres:", className='mb-2'),
                dcc.Dropdown(
                    id='mode-hes',
                    options=[
                        {'label': 'Call', 'value': 'Calls'},
                        {'label': 'Put', 'value': 'Puts'}
                    ],
                    value='Calls',
                    className='mb-3'
                )
            ], width=4)
        ]),
        dbc.Row([
            dbc.Col(html.Button('Calculer Prix avec Heston', id='calculate-heston-button', className='btn-primary btn-lg'), width={"size": 2, "offset": 5})
        ]),
        dcc.Loading(
            id="loading-1",
            type="default",  # Vous pouvez choisir parmi 'graph', 'cube', 'circle', 'dot', ou 'default'
            children=html.Div(id='heston-result')
        )
    ], fluid=True)
    
def layout_monte_carlo_heston():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H1("Monte Carlo - Modèle Heston", className='text-center mb-4'), width=12)),
        dbc.Row([
            dbc.Col(card_input('S', 'S-input-mc-heston', 187), width=4),
            dbc.Col(card_input('K (Prix d\'exercice de l\'option)', 'K-input-mc-heston', 180), width=4),
            dbc.Col(card_input('T (Maturité)', 'T-input-mc-heston', 1), width=4)
        ]),
    
        dbc.Row([
            dbc.Col(card_input('r (Taux sans risque)', 'r-input-mc-heston', 0.05), width=3),
            dbc.Col(card_input('d (div)', 'd-input-mc-heston', 0.05), width=3),
            dbc.Col(card_input('theta', 'theta-input-mc-heston', 0.035), width=3),
            dbc.Col(card_input('rho', 'rho-input-mc-heston', -1), width=3),
            dbc.Col(card_input('kappa', 'kappa-input-mc-heston', 3.32), width=3),
            dbc.Col(card_input('xi', 'xi-input-mc-heston', 0.62), width=3),
            dbc.Col(card_input('sigma0', 'sigma-input-mc-heston', 0.23), width=3),
            dbc.Col(card_input('Nombre de Simulations', 'num-simulations-heston', 10000), width=3)
        ]),   
    
        dbc.Row([
            dbc.Col([
                html.H5("Choisir le type d'option exotique:", className='mb-2'),
                dcc.Dropdown(
                    id='exotic-option-type-dropdown-heston',
                    options=[
                        {'label': 'Call Européen', 'value': 'europeanCall'},
                        {'label': 'Put Européen', 'value': 'europeanPut'},
                        {'label': 'Call Asiatique', 'value': 'asiaticCall'},
                        {'label': 'Put Asiatique', 'value': 'asiaticPut'},
                        {'label': 'LookBack Max', 'value': 'lookBackMax'},
                        {'label': 'LookBack Min', 'value': 'lookBackMin'}
                    ],
                    value='europeanCall',
                    className='mb-3'
                )
            ], width=4)
        ]),
        
        dbc.Row([
            dbc.Col(html.Button('Calculer Prix avec Monte Carlo Heston', id='calculate-mc-heston-button', className='btn-primary btn-lg'), width={"size": 2, "offset": 5})
        ]),
        dcc.Loading(
            id="loading-1",
            type="default", 
            children=html.Div(id='monte-carlo-heston-result')
        )
    ], fluid=True)
    
    
data = {'Instrument': ['Prix du Bond', 'Jambe fixe du Swap', 'Jambe Variable du Swap', 'Prix du Swap','Taux Swap'],
        'Value': [0.0, 0.0, 0.0, 0.0,0.0]}
df = pd.DataFrame(data)
def layout_hull_white_rates():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H1("Modèle de taux Hull-White", className='text-center mb-4'), width=12)),
        dbc.Row([
            
            dbc.Col(card_input('Theta (Moyenne à long terme)', 'theta-input', 0.1), width=4),
            dbc.Col(card_input(' Alpha (Vitesse de retour à la moyenne)', 'alpha-input', 0.5), width=4),
            dbc.Col(card_input('Sigma  (Volatilité)', 'sigma-input',0.02 ), width=4)
        ]),
        dbc.Row([
            dbc.Col(card_input('Nombre de trajectoires', 'num-paths-input', 1000), width=4),
            dbc.Col(card_input('Maturité (en années)', 'T-input', 1), width=4), 

            dbc.Row([
                        dbc.Col(html.H5('Payments (separés par des virgules)'), md=12),
                        dbc.Col(dbc.Input(id='payment-input', type='text', placeholder='Enter payments', value='0.25,0.5,0.75,1'), md=4),
                        dbc.Col(card_input('Nominal','N-input',1),width =4),
                        dbc.Col(card_input('Taux fixe K','K-input',0.05),width=4)
                    ]),

            dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    dash_table.DataTable(
                        id='results-table',
                        columns=[
                            {'name': 'Instrument', 'id': 'Instrument'},
                            {'name': 'Value', 'id': 'Value', 'type': 'numeric', 'format': {'specifier': '.4f'}}
                        ],
                        data=df.to_dict('records'),)])])),
            ]),
        dbc.Row([
            dbc.Col(html.Button('Afficher quelques courbes de taux', id='simulate-button-hw', className='btn-primary btn-lg'), width={"size": 2, "offset": 5})]),
        dbc.Row(dbc.Col(dcc.Graph(id='interest-rate-graph',style={'height': '400px', 'width': '100%'}))),

    ], fluid=True)
    
    
def layout_readme():
    readme_content = read_readme()
    return dbc.Container([
        dbc.Row(dbc.Col(dcc.Markdown(readme_content), width=12))
    ], fluid=True)
# Définition des onglets
tabs = dbc.Tabs(
    [
        dbc.Tab(label="Black-Scholes Vol. Constante", tab_id="tab-bs"),
        dbc.Tab(label="Monte Carlo - BS Vol. Constante", tab_id="tab-mc"),
        dbc.Tab(label="Black-Scholes avec Smile de Volatilité", tab_id="tab-smile"),
        dbc.Tab(label="Heston Calibrée ", tab_id="tab-heston"),
        dbc.Tab(label="Monte Carlo - Heston ", tab_id="tab-mc-heston"),
        dbc.Tab(label='Taux avec Hull-White',tab_id = 'tab-hull-white'),
        dbc.Tab(label='README', tab_id='tab-readme')
    ],
    id="tabs",
    active_tab="tab-bs",
)

# Mise en page principale
app.layout = dbc.Container(
    [
        html.H1("Asset pricing", className='text-center mb-4'),
        tabs,
        html.Div(id="content")
    ],
    fluid=True
)

# Callback pour changer de vue
@app.callback(Output("content", "children"), [Input("tabs", "active_tab")])
def switch_tab(at):
    if at == "tab-bs":
        return layout_black_scholes_vol_constante()
    elif at == "tab-smile":
        return layout_black_scholes_vol_smile()
    elif at == "tab-mc":
        return layout_monte_carlo_bs_vol_constante()
    elif at == "tab-heston":
        return layout_heston_calibre()
    elif at == "tab-mc-heston":
        return layout_monte_carlo_heston()
    elif at == 'tab-hull-white' :
        return layout_hull_white_rates()
    elif at == 'tab-readme':
        return layout_readme()

    return html.P("Ceci est le contenu par défaut")

@lru_cache
def get_vanilla_pricer_with_smile (market_date, ticker, mode, r, d):
    return VanillaPricerWithsmiles(market_date, ticker, mode, r, d)

@lru_cache
def get_vanilla_pricer_heston(market_date, ticker, mode, r, d):
    return VanillaPricerWithHestonCalibrated(market_date, ticker, mode, r, d)

@lru_cache
def get_heston(market_date, ticker, mode, r, d):
    return HestonCalibrator(market_date, ticker, mode, r, d)

@app.callback(
    Output('results-output-smile', 'children'),
    [Input('calculate-button-smile', 'n_clicks')],
    [State('stock-ticker-input', 'value'),
     Input('K-input-smile', 'value'),
     Input('T-input-smile', 'value'),
     Input('r-input-smile', 'value'),
     Input('d-input-smile', 'value'),
     State('option-type-dropdown', 'value'),
     State('mode', 'value'),
     State('K2-input-smile', 'value'),
     State('K3-input-smile', 'value')]
)
def update_output_smile(n_clicks,ticker, K, T, r, d, option_type,mode, K2, K3):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    try:
        market_date= (datetime.datetime.today() - BDay(1)).date()
        
        # pricer = VanillaPricerWithsmiles(market_date, ticker, mode, r, d)
        pricer = get_vanilla_pricer_with_smile (market_date, ticker, mode, r, d)

        if option_type in ['call', 'put', 'straddle']:
            price = pricer.PriceStrategy(option_type, K, T)
            
        elif option_type == 'callSpread':
        # Vérifiez que K2 est disponible et non nul
            if K2 is None:
                return html.Div("Veuillez fournir le second prix d'exercice pour le Call Spread.")
            price = pricer.PriceStrategy(option_type, K, float(K2), T)
        elif option_type == 'butterfly':
            # Vérifiez que K2 et K3 sont disponibles et non nuls
            if K2 is None or K3 is None:
                return html.Div("Veuillez fournir les deuxième et troisième prix d'exercice pour le Butterfly.")
            price = pricer.PriceStrategy(option_type, K, float(K2), float(K3), T)
        else:
            return html.Div("Type d'option non reconnu.")
              
        S = pricer.stock_price 
        implied_vol = pricer.ImpliedVol(K, T)
        

        return html.Div([
            html.H3('Résultats:'),
            html.P(f"Prix de la stratégie: {price:.4f}"),
            html.P(f"Prix de l'actif sous-jacent (S): {S:.2f}"),
            html.P(f"Volatilité Implicite: {implied_vol:.4f}")
        ])
    except Exception as e:
        return html.Div(f"Une erreur est survenue : {e}")
    
@app.callback(
    Output('volatility-surface', 'style'),
    [Input('calculate-button-smile', 'n_clicks')]
)
def show_vol_surface(n_clicks):
    if n_clicks and n_clicks > 0:
        return {}  # Style vide pour afficher le graphique
    else:
        return {'display': 'none'}

@app.callback(
    Output('volatility-surface', 'figure'),
    [Input('show-vol-surface-button', 'n_clicks')],
    [State('stock-ticker-input', 'value'),
     State('r-input-smile', 'value'),
     State('d-input-smile', 'value'),
     State('mode', 'value')]
)
def update_vol_surface(n_clicks,ticker,r,d, mode):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    
    try:
        market_date = (datetime.datetime.today() - BDay(1)).date()
        pricer = get_vanilla_pricer_with_smile (market_date, ticker, mode, r, d)
        
        stock_price = pricer.stock_price

        K_min = stock_price * 0.8  
        K_max = stock_price * 1.2  
        K_range = np.linspace(K_min, K_max, 40)
        T_range = np.linspace(0.1, 2, 20)   

        vol_surface = [[pricer.ImpliedVol(K_val, T_val) for K_val in K_range] for T_val in T_range]

        fig = go.Figure(data=[go.Surface(z=vol_surface, x=K_range, y=T_range,colorscale='Blues')])
        fig.update_layout(
            title='Surface de Volatilité Implicite',
            autosize=True,
            scene=dict(
                xaxis_title='K',
                yaxis_title='T',
                zaxis_title='Vol Implicite'
            )
        )
        return fig 
    except Exception as e:
        return go.Figure() 
    
@app.callback(
    Output('greeks-output-smile', 'children'),
    [Input('calculate-greeks-button', 'n_clicks')],
    [State('stock-ticker-input', 'value'),
     State('K-input-smile', 'value'),
     State('T-input-smile', 'value'),
     State('r-input-smile', 'value'),
     State('d-input-smile', 'value'),
     State('option-type-dropdown', 'value'),
     State('mode', 'value'),
     State('K2-input-smile', 'value'),
     State('K3-input-smile', 'value')]
)
def calculate_greeks_smile(n_clicks, ticker, K, T, r, d, option_type, mode, K2, K3):
    if n_clicks is None:
        return html.Div()  # Pas de clic, pas de calcul

    try:
        market_date = (datetime.datetime.today() - BDay(1)).date()
        pricer = get_vanilla_pricer_with_smile(market_date, ticker, mode, r, d)
        greeks = ["delta", "gamma", "vega", "theta", "rho"]
        results = []

        args = [K, T]
        if option_type == 'callSpread' or option_type == 'butterfly':
            args.extend([K2, K3])

        for greek in greeks:
            greek_value = pricer.GreekForStrategy(option_type, greek, *args)
            results.append(html.P(f"{greek.capitalize()}: {greek_value:.4f}"))

        return html.Div(results)
    except Exception as e:
        return html.Div(f"Une erreur est survenue lors du calcul des Grecques : {e}")


@app.callback(
    [Output('K2-container', 'style'), Output('K3-container', 'style')],
    [Input('option-type-dropdown', 'value')]
)
def toggle_strike_input_visibility(option_type):
    if option_type == 'callSpread':
        return {'display': 'block'}, {'display': 'none'}
    elif option_type == 'butterfly':
        return {'display': 'block'}, {'display': 'block'}
    else:
        return {'display': 'none'}, {'display': 'none'}

@app.callback(
    Output('results-output-bs', 'children'),
    [Input('calculate-button-bs', 'n_clicks')],
    [State('S-input', 'value'),
     State('K-input', 'value'),
     State('T-input', 'value'),
     State('sigma-input', 'value'),
     State('r-input', 'value'),
     State('d-input', 'value'),
     State('option-type-dropdown', 'value'),
     State('K2-input', 'value'),
     State('K3-input', 'value')]
)
def update_output_bs(n_clicks, S, K, T, sigma, r, d, option_type, K2, K3):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate

    try:
        model = VanillaPricerWithConstanteVol(sigma, r, d, S)
        if option_type in ['call', 'put', 'straddle']:
            price = model.PriceStrategy(option_type, K, T)
        elif option_type == 'callSpread':
            # Vérifiez que K2 est disponible et non nul
            if K2 is None:
                return html.Div("Veuillez fournir le second prix d'exercice pour le Call Spread.")
            price = model.PriceStrategy(option_type, K, float(K2), T)
        elif option_type == 'butterfly':
            # Vérifiez que K2 et K3 sont disponibles et non nuls
            if K2 is None or K3 is None:
                return html.Div("Veuillez fournir les deuxième et troisième prix d'exercice pour le Butterfly.")
            price = model.PriceStrategy(option_type, K, float(K2), float(K3), T)
        else:
            return html.Div("Type d'option non reconnu.")

        return html.Div([
            html.H3('Résultats:'),
            html.P(f"Prix de la stratégie sélectionnée: {price:.4f}")
        ])
    except Exception as e:
        return html.Div(f"Une erreur est survenue : {e}")
    
@app.callback(
    Output('greeks-output', 'children'),
    [Input('calculate-greeks-button', 'n_clicks')],
    [State('S-input', 'value'),
     State('K-input', 'value'),
     State('T-input', 'value'),
     State('sigma-input', 'value'),
     State('r-input', 'value'),
     State('d-input', 'value'),
     State('option-type-dropdown', 'value'),
     State('K2-input', 'value'),
     State('K3-input', 'value')]
)
def calculate_greeks(n_clicks, S, K, T, sigma, r, d, option_type, K2, K3):
    if n_clicks is None:
        return html.Div()  

    model = VanillaPricerWithConstanteVol(sigma, r, d, S)
    greeks = ["delta", "gamma", "vega", "theta", "rho"]
    results = []

    try:
        args = [K, T]
        if option_type in ['callSpread', 'butterfly']:
            args.extend([K2, K3])

        for greek in greeks:
            if option_type in ['call', 'put', 'straddle']:
                greek_value = model.GreekForStrategy(option_type, greek, *args)
            elif option_type == 'callSpread':
                if K2 is None:
                    return html.Div("Veuillez fournir le second prix d'exercice pour le Call Spread.")
                greek_value = model.GreekForStrategy(option_type, greek, *args)
            elif option_type == 'butterfly':
                if K2 is None or K3 is None:
                    return html.Div("Veuillez fournir les deuxième et troisième prix d'exercice pour le Butterfly.")
                greek_value = model.GreekForStrategy(option_type, greek, *args)
            else:
                return html.Div("Type d'option non reconnu.")

            results.append(html.P(f"{greek.capitalize()}: {greek_value:.4f}"))

        return html.Div(results)
    except Exception as e:
        return html.Div(f"Une erreur est survenue lors du calcul des Grecques : {e}")

    
@app.callback(
    Output('monte-carlo-result', 'children'),
    [Input('calculate-mc-button', 'n_clicks')],
    [State('S-input-mc', 'value'),
     State('K-input-mc', 'value'),
     State('T-input-mc', 'value'),
     State('sigma-input-mc', 'value'),
     State('r-input-mc', 'value'),
     State('d-input-mc', 'value'),
     State('num-simulations', 'value'),
     State('exotic-option-type-dropdown', 'value')]
)
def calculate_monte_carlo_bs_price(n_clicks, S, K, T, sigma, r,d, num_simulations, option_type):
    if n_clicks is None:
        return html.Div()  

    if option_type == 'europeanCall':
        model = MonteCarloCallPricerBS(S, r, d, sigma, T, K, num_simulations, True)
    elif option_type == 'europeanPut':
        model = MonteCarloPutPricerBS(S, r, d, sigma, T, K, num_simulations, True)
    elif option_type == 'asiaticCall':
        model = MonteCarloAsiaticCallPricerBS(S, r, d, sigma, T, K, num_simulations, True)
    elif option_type == 'asiaticPut':
        model = MonteCarloAsiaticPutPricerBS(S, r, d, sigma, T, K, num_simulations, True)
    elif option_type == 'lookBackMax':
        model = MonteCarloLookBackMaxPricerBS(S, r, d, sigma, T, K, num_simulations, True)
    elif option_type == 'lookBackMin':
        model = MonteCarloLookBackMinPricerBS(S, r, d, sigma, T, K, num_simulations, True)
    monte_carlo_price = model.price()

    return html.Div([
        html.H3('Résultat du Pricing Monte Carlo:'),
        html.P(f"Prix Calculé pour {option_type}: {monte_carlo_price:.2f}")
    ])

@app.callback(
    Output('heston-result', 'children'),
    Input('calculate-heston-button', 'n_clicks'),
    [State('stock-ticker-input-hes', 'value'),
     State('K-input-heston', 'value'),
     State('T-input-heston', 'value'),
     State('r-input-heston', 'value'),
     State('d-input-heston', 'value'),
     State('option-type-dropdown', 'value'),
     State('mode-hes', 'value'),
     State('K2-input-smile-hes', 'value'),
     State('K3-input-smile-hes', 'value')]
)

def calculate_Heston_price(n_clicks,ticker,  K, T, r, d, option_type, mode, K2, K3):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    try:
        market_date= (datetime.datetime.today() - BDay(1)).date()
        pricer = get_vanilla_pricer_heston(market_date, ticker, mode, r, d)
        theta, rho, kappa, xi, sigma = pricer.calibratedparams
        if option_type in ['call', 'put', 'straddle']:
            price = pricer.PriceStrategy(option_type, K, T)
            
        elif option_type == 'callSpread':
        # Vérifiez que K2 est disponible et non nul
            if K2 is None:
                return html.Div("Veuillez fournir le second prix d'exercice pour le Call Spread.")
            price = pricer.PriceStrategy(option_type, K, float(K2), T)
        elif option_type == 'butterfly':
            # Vérifiez que K2 et K3 sont disponibles et non nuls
            if K2 is None or K3 is None:
                return html.Div("Veuillez fournir les deuxième et troisième prix d'exercice pour le Butterfly.")
            price = pricer.PriceStrategy(option_type, K, float(K2), float(K3), T)
        else:
            return html.Div("Type d'option non reconnu.")
              
        S = pricer.stock_price 
        

        return html.Div([
            html.H3('Résultats:'),
            html.P(f"Prix Calculé pour {option_type}: {price:.2f}"),
            html.P(f"Prix de l'actif sous-jacent (S): {S:.2f}"),
            html.H5('Paramètres Calibrés:'),
            html.P(f"theta: {theta:.4f}"),
            html.P(f"rho: {rho:.4f}"),
            html.P(f"kappa: {kappa:.4f}"),
            html.P(f"xi: {xi:.4f}"),
            html.P(f"sigma0: {sigma:.4f}")
        ])
    except Exception as e:
        return html.Div(f"Une erreur est survenue : {e}")

@app.callback(
    Output('monte-carlo-heston-result', 'children'),
    [Input('calculate-mc-heston-button', 'n_clicks')],
    [
     State('S-input-mc-heston', 'value'),
     State('K-input-mc-heston', 'value'),
     State('T-input-mc-heston', 'value'),
     State('r-input-mc-heston', 'value'),
     State('d-input-mc-heston', 'value'),
     State('theta-input-mc-heston', 'value'),
     State('rho-input-mc-heston', 'value'),
     State('kappa-input-mc-heston', 'value'),
     State('xi-input-mc-heston', 'value'),
     State('sigma-input-mc-heston', 'value'),
     State('num-simulations-heston', 'value'),
     State('exotic-option-type-dropdown-heston', 'value')]
)
def calculate_monte_carlo_Heston_price(n_clicks,S,  K, T, r,d,theta, rho, kappa, xi, sigma, num_simulations, option_type):
    if n_clicks is None:
        return html.Div()  
    
    #market_date = (datetime.datetime.today() - BDay(1)).date()
    #Calibrator = get_heston(market_date, ticker, mode, r, d)
    #price = Calibrator.S
    #sigma, kappa, theta, rho, xi= Calibrator.HestonParameters()
    if option_type == 'europeanCall':
        model = MonteCarloCallPricerHeston(S, K,r, d, sigma, kappa, theta, rho, xi, T, num_simulations, True)
    elif option_type == 'europeanPut':
        model = MonteCarloPutPricerHeston(S, K,r, d, sigma, kappa, theta, rho, xi, T, num_simulations, True)
    elif option_type == 'asiaticCall':
        model = MonteCarloAsiaticCallPricerHeston(S, K,r, d, sigma, kappa, theta, rho, xi, T, num_simulations, True)
    elif option_type == 'asiaticPut':
        model = MonteCarloAsiaticPutPricerHeston(S, K,r, d, sigma, kappa, theta, rho, xi, T, num_simulations, True)
    elif option_type == 'lookBackMax':
        model = MonteCarloLookBackMaxPricerHeston(S, K,r, d, sigma, kappa, theta, rho, xi, T, num_simulations, True)
    elif option_type == 'lookBackMin':
        model = MonteCarloLookBackMinPricerHeston(S, K,r, d, sigma, kappa, theta, rho, xi, T, num_simulations, True)
    monte_carlo_price = model.price()

    return html.Div([
        html.H3('Résultat du Pricing Monte Carlo:'),
        html.P(f"Prix Calculé pour {option_type}: {monte_carlo_price:.2f}"),
    ])


@app.callback(
    Output('interest-rate-graph', 'figure'),
    [Input('simulate-button-hw', 'n_clicks')],
    [Input('theta-input', 'value'),
     Input('alpha-input', 'value'),
     Input('sigma-input', 'value'),
     Input('num-paths-input','value'),
     Input('T-input', 'value')]
)
def update_output_hw(n_clicks,theta,alpha,sigma,num_paths,T,num_steps=252):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    try:
        hw = HullWhite(theta,alpha,sigma)
        short_rate_paths = hw.sim_process(T,num_steps,num_paths)
        figure = {
            'data': [
                {'x': list(np.arange(num_steps + 1) * T / num_steps), 'y': short_rate_paths[i, :], 'type': 'line', 'name': f'Path {i+1}'}
                for i in range(5)
            ],
            'layout': {
                'title': 'Simulated Interest Rate Curve',
                'xaxis': {'title': 'Time Step'},
                'yaxis': {'title': 'Interest Rate'},
            }
        }

        return figure
    except Exception as e:
        return html.Div(f"Une erreur est survenue : {e}")
    
@app.callback(
    Output('bond-price-output', 'children'),
    [Input('simulate-button-hw', 'n_clicks')],
    [Input('theta-input', 'value'),
     Input('alpha-input', 'value'),
     Input('sigma-input', 'value'),
     Input('num-paths-input','value'),
     Input('T-input', 'value')]
)
def update_bond_price(n_clicks, theta, alpha, sigma,num_paths, T,num_steps=252):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate

    try:
        # Calculate and return bond price based on your logic
        hw = HullWhite(theta,alpha,sigma)
        short_rate_paths = hw.sim_process(T,num_steps,num_paths)
        bond = BondPricing(hw)
        bond_price = bond.price_zero_coupon_bond(T,short_rate_paths)
        return f'Bond Price: {bond_price:.2f}'

    except Exception as e:
        print(f"Error: {e}")
        return dash.no_update

# Similarly, create callback functions for the fixed leg, variable leg, and swap price
@app.callback(
    Output('results-table', 'data'),
    [Input('simulate-button-hw', 'n_clicks')],
    [Input('theta-input', 'value'),
     Input('alpha-input', 'value'),
     Input('sigma-input', 'value'),
     Input('num-paths-input','value'),
     Input('T-input', 'value'),
     Input('N-input','value'),
     Input('K-input','value'),
     Input('payment-input','value')]

)
def update_results_table(n_clicks, theta, alpha, sigma, num_paths,T,N,K,payment, num_steps=252):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    
    # Perform your calculations and update the table data accordingly
    # Replace the following lines with your actual calculations
    payment = list(map(float, payment.split(',')))
    hw = HullWhite(theta,alpha,sigma)
    short_rate_paths = hw.sim_process(T,num_steps,num_paths)
    bond = BondPricing(hw)
    bond_price = bond.price_zero_coupon_bond(T,short_rate_paths)
    fixed_leg_price =bond.price_fixed_leg_swap(N,K,payment,short_rate_paths)
    variable_leg_price = bond.price_var_leg_swap(N,payment,short_rate_paths)
    swap_price = bond.swap_price(N,K,payment,short_rate_paths)
    taux_swap = bond.taux_swap(payment,short_rate_paths)
    
    data = {'Instrument': ['Prix du Bond', 'Jambe fixe du Swap', 'Jambe Variable du Swap', 'Prix du Swap','Taux Swap'],
            'Value': [bond_price, fixed_leg_price, variable_leg_price, swap_price,taux_swap]}
    
    return pd.DataFrame(data).to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)