from binance.client import Client
import pandas as pd
from decouple import config


api = config("TEST_API")
api_secret = config("TEST_API_SECRET")

client = Client(api,api_secret,tld="com",testnet=True)

class Bot:
    def __init__(self,symbol,volume,no_of_safty_orders,proportion,profit_target):
        self.symbol = symbol
        self.volume = volume
        self.no_of_safty_orders = no_of_safty_orders
        self.proportion = proportion
        self.profit_target = profit_target

    def get_balance(self):
        x = client.get_account()
        df = pd.DataFrame(x['balances'])
        print(df)

    def get_curr_value(self,symbol):
        price = client.get_symbol_ticker(symbol=symbol)
        return price["price"]

    def market_order(self,symbol, volume, direction):
        if direction == "buy":
            order = client.create_order(
                symbol=symbol,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=volume
            )

            return order['fills']
        if direction == "sell":
            order = client.create_order(
                symbol=symbol,
                side=Client.SIDE_SELL,
                type=Client.ORDER_TYPE_MARKET,
                quantity=volume
            )
            print(order['fills'])

    # df1 = pd.DataFrame(columns=['price','qty'])
    # df2 = pd.DataFrame(columns=['price','qty'])
    #
    #
    # while True:
    #     x = market_order("BTCUSDT",0.001,"buy")
    #     df2.loc[0,'price'] = float(x[0]['price'])
    #     df2.loc[0, 'qty'] = float(x[0]['qty'])
    #     df1 = pd.concat([df1,df2],ignore_index=True)
    #     print(df1)

    def cal_dev_from_initial_price(self,symbol, df):
        curr_price = float(self.get_curr_value(symbol))
        init_price = float(df.price[0])
        pct_change = ((curr_price - init_price) / init_price) * 100
        return pct_change

    def cal_pct_profit(self,symbol, df):
        total_profit = 0
        total_value_of_coins = 0
        current_price = float(self.get_curr_value(symbol))

        for index in df.index:
            initial_value = float(df.loc[index, "price"]) * float(df.loc[index, "qty"])
            current_value = current_price * float(df.loc[index, "qty"])
            profit = current_value - initial_value
            total_profit += profit
            total_value_of_coins += initial_value
        return (total_profit / total_value_of_coins) * 100

    def sell_all(self,symbol, df):
        volume = float(df["qty"].sum())
        self.market_order(symbol, volume, "sell")

    def run(self):
        while True:
            df1 = pd.DataFrame(columns=['price', 'qty'])
            df2 = pd.DataFrame(columns=['price', 'qty'])
            x = self.market_order(self.symbol, self.volume, "buy")
            df2.loc[0, 'price'] = float(x[0]['price'])
            df2.loc[0, 'qty'] = float(x[0]['qty'])
            df1 = pd.concat([df1, df2], ignore_index=True)

            curr_no_of_safty_orders = 0
            multiplied_volume = self.volume * 2
            deviation = -1
            next_price_level = -1

            while True:
                dev = self.cal_dev_from_initial_price(self.symbol, df1)
                print(f"Deviation : {dev}")
                if dev <= next_price_level * self.proportion:
                    if curr_no_of_safty_orders < self.no_of_safty_orders:
                        try:
                            x = self.market_order(self.symbol, multiplied_volume, "buy")
                            df2.loc[0, 'price'] = float(x[0]['price'])
                            df2.loc[0, 'qty'] = float(x[0]['qty'])
                            df1 = pd.concat([df1, df2], ignore_index=True)
                        except:
                            pass

                        multiplied_volume *= 2
                        deviation *= 2
                        next_price_level += deviation
                        curr_no_of_safty_orders += 1

                pct_profit = self.cal_pct_profit(self.symbol, df1)
                print(f"pct_profit : {pct_profit}")
                print(df1)
                if pct_profit >= self.profit_target:
                    self.sell_all(self.symbol, df1)
                    break
