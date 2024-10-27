
import pandas as pd
import yfinance as yf
import datetime 

class DataImporter():
    """
    Classe pour importer des données liées aux options et aux prix des actions.
    """
    def __init__(self, ticker:str, market_date:datetime.datetime):
        """
        Initialise l'instance avec le ticker de l'action et la date du marché.

        Paramètres :
        ticker (str) : Symbole boursier de l'action.
        market_date (datetime.datetime) : Date du marché pour laquelle les données seront récupérées.
        """
        self.ticker = yf.Ticker(ticker)
        self.market_date = market_date
        
    def get_stock_price(self):
        
        start_date, end_date = self.market_date,  self.market_date + datetime.timedelta(days = 1)
        
        return self.ticker.history(start = start_date, end = end_date)['Close'][0]
 
    def get_all_options_data(self):
           
        """
        Récupère toutes les données sur les options (appels et mises) disponibles.

        Retourne :
        pandas.DataFrame : DataFrame contenant toutes les données sur les appels.
        pandas.DataFrame : DataFrame contenant toutes les données sur les mises.
        """
        all_calls = []
        all_puts = []
        for expiration in self.ticker.options:
            options_chain = self.ticker.option_chain(expiration)
            call_data = pd.DataFrame(options_chain.calls)
            put_data = pd.DataFrame(options_chain.puts)

            call_data['Expiration'] = expiration  
            put_data['Expiration'] = expiration  

            all_calls.append(call_data)
            all_puts.append(put_data)

        all_calls_df = pd.concat(all_calls, ignore_index=True)
        all_puts_df = pd.concat(all_puts, ignore_index=True)

        all_calls_df['Market_Date'] = [ t.date() for t in list(all_calls_df['lastTradeDate'])]
        all_calls_df['Expiration_Date'] = [datetime.datetime.strptime(sd, "%Y-%m-%d").date() for sd in list(all_calls_df['Expiration'])]

        all_puts_df['Market_Date'] = [ t.date() for t in list(all_puts_df['lastTradeDate'])]
        all_puts_df['Expiration_Date'] = [datetime.datetime.strptime(sd, "%Y-%m-%d").date() for sd in list(all_puts_df['Expiration'])]

        all_calls_df['T'] = [(ed - self.market_date).days/365. for ed in list(all_calls_df['Expiration_Date'])]
        all_puts_df['T'] = [(ed - self.market_date).days/365. for ed in list(all_puts_df['Expiration_Date'])]

        return all_calls_df, all_puts_df

    def get_options_data_filtered(self):  
        
        all_calls_df, all_puts_df = self.get_all_options_data()
        puts_df = all_puts_df[all_puts_df.Market_Date == self.market_date]
        calls_df = all_calls_df[all_calls_df.Market_Date == self.market_date]   
        return calls_df, puts_df        

    def get_options_data_expiry(self, expiration_index:str):
      
        options_expiration = self.ticker.options[expiration_index]
        call_info = pd.DataFrame(self.ticker.option_chain(options_expiration)[0])
        put_info = pd.DataFrame(self.ticker.option_chain(options_expiration)[1])
        return call_info, put_info
    
    def get_expiries(self):
        return set(self.ticker.options)
