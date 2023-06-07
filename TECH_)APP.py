# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 13:01:52 2023
@author: ms.sohn
"""

from flask import Flask, render_template
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/usstock')
def usstock():
    today = datetime.today()
    day = timedelta(90)

    # Get the data from https://www.nasdaq.com/market-activity/stocks/screener
    file = "major_list.csv"
    Excel_data = pd.read_csv(file)

    stocklist = []
    stocklist_df = []

    for i in range(len(Excel_data)):
        Ticker = Excel_data['Symbol'][i]
        try:
            px_data = yf.download(Ticker, today - day, today + timedelta(-1))
            digit = float(px_data['Open'].iloc[1])
            print(digit)
            stocklist.append(Ticker)
            stocklist_df.append(px_data)
        except:
            pass

    class cal:
        def __init__(self):
            self.RSI_SIG_DAYS_U = 0
            self.RSI_SIG_DAYS_D = 0
            self.RSI_SIG_DAYS = 0
            self.RSI_SIG = 0
            self.BOLL_SIG = 0
            self.BOLL_SIG_DAYS_U = 0
            self.BOLL_SIG_DAYS_D = 0
            self.BOLL_WD = 0
            self.BOLL_WD_DAYS = 0
            self.BOLL_RVS = 0
            self.BOLL_RVS_DAYS = 0
            self.BOLL_MMT = 0
            self.BOLL_MMT_DAYS = 0
            self.LIST = []

        def setter(self, x):
            self.TIC = x
            num = stocklist.index(self.TIC)
            df_origin = stocklist_df[num].tail(90)
            df = df_origin.copy()
            self.UP = df['Close'].rolling(window=20).mean() + 2 * df['Close'].rolling(window=20).std()
            self.LW = df['Close'].rolling(window=20).mean() - 2 * df['Close'].rolling(window=20).std()
            self.MD = df['Close'].rolling(window=20).mean()
            self.Close = df['Close']
            self.RSI = self.calculate_rsi(df['Close'], 14)

        def calculate_rsi(self, prices, window=14):
            delta = prices.diff()
            up = delta.copy()
            down = delta.copy()
            up[up < 0] = 0
            down[down > 0] = 0
            avg_gain = up.rolling(window).mean()
            avg_loss = abs(down.rolling(window).mean())
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return rsi

        def get_rsi(self):
            for i in range(1, 6):
                if self.RSI.iloc[-i] > 80:
                    self.RSI_SIG_DAYS_U += 1

                if self.RSI.iloc[-i] < 20:
                    self.RSI_SIG_DAYS_D += 1

            if self.RSI.iloc[-1] > 80:
                self.RSI_SIG -= 1
                self.RSI_SIG_DAYS = self.RSI_SIG_DAYS_U
            elif self.RSI.iloc[-1] > 70:
                self.RSI_SIG -= 0.5
                self.RSI_SIG_DAYS = self.RSI_SIG_DAYS_U
            elif self.RSI.iloc[-1] < 20:
                self.RSI_SIG += 1
                self.RSI_SIG_DAYS = self.RSI_SIG_DAYS_D
            elif self.RSI.iloc[-1] < 30:
                self.RSI_SIG += 0.5

        def get_boll(self):
            if self.Close.iloc[-1] > self.UP.iloc[-1]:
                self.BOLL_SIG = 1
            elif self.Close.iloc[-1] < self.LW.iloc[-1]:
                self.BOLL_SIG = -1

            for i in range(1, 6):
                if self.Close.iloc[-i] > self.UP.iloc[-i]:
                    self.BOLL_SIG_DAYS_U += 1

                if self.Close.iloc[-i] < self.LW.iloc[-i]:
                    self.BOLL_SIG_DAYS_D += 1

            if self.BOLL_SIG == 1 or self.BOLL_SIG_DAYS_U > 0:
                if self.UP.iloc[-1] - self.LW.iloc[-1] > self.UP.iloc[-2] - self.LW.iloc[-2]:
                    self.BOLL_WD = 1
                elif self.UP.iloc[-1] - self.LW.iloc[-1] < self.UP.iloc[-2] - self.LW.iloc[-2]:
                    self.BOLL_WD = -1

            if self.LW.iloc[-1] > self.LW.iloc[-2]:
                self.BOLL_RVS = -1

            if (self.LW.iloc[-1] - self.LW.iloc[-2] / abs(self.LW.iloc[-2])) < (
                    self.LW.iloc[-2] - self.LW.iloc[-3] / abs(self.LW.iloc[-3])):
                self.BOLL_MMT = -1

            for i in range(1, 6):
                if self.UP.iloc[-i] - self.LW.iloc[-i] > self.UP.iloc[-i - 1] - self.LW.iloc[-i - 1]:
                    self.BOLL_WD_DAYS += 1

                if self.LW.iloc[-i] < self.LW.iloc[-i - 1]:
                    self.BOLL_RVS_DAYS += 1

                if (self.LW.iloc[-1] - self.LW.iloc[-2] / abs(self.LW.iloc[-2])) < (
                        self.LW.iloc[-2] - self.LW.iloc[-3] / abs(self.LW.iloc[-3])):
                    self.BOLL_MMT_DAYS += 1

            if self.BOLL_SIG == -1 or self.BOLL_SIG_DAYS_D > 0:
                if self.UP.iloc[-1] - self.LW.iloc[-1] > self.UP.iloc[-2] - self.LW.iloc[-2]:
                    self.BOLL_WD = -1
                elif self.UP.iloc[-1] - self.LW.iloc[-1] < self.UP.iloc[-2] - self.LW.iloc[-2]:
                    self.BOLL_WD = +1

            if self.UP.iloc[-1] < self.UP.iloc[-2]:
                self.BOLL_RVS = 1

            if (self.UP.iloc[-1] - self.UP.iloc[-2] / abs(self.UP.iloc[-2])) > (
                    self.UP.iloc[-2] - self.UP.iloc[-3] / abs(self.UP.iloc[-3])):
                self.BOLL_MMT = 1

            for i in range(1, 6):
                if self.UP.iloc[-i] - self.LW.iloc[-i] > self.UP.iloc[-i - 1] - self.LW.iloc[-i - 1]:
                    self.BOLL_WD_DAYS += 1

                if self.UP.iloc[-i] > self.UP.iloc[-i - 1]:
                    self.BOLL_RVS_DAYS += 1

                if (self.UP.iloc[-1] - self.UP.iloc[-2] / abs(self.UP.iloc[-2])) > (
                        self.UP.iloc[-2] - self.UP.iloc[-3] / abs(self.UP.iloc[-3])):
                    self.BOLL_MMT_DAYS += 1

        def get_result(self):
            self.Revision_SIG = self.BOLL_WD + self.BOLL_RVS + self.BOLL_MMT + self.RSI_SIG
            self.LIST = [self.BOLL_SIG, self.BOLL_WD, self.BOLL_RVS, self.BOLL_RVS_DAYS, self.BOLL_MMT,
                         int(self.RSI.iloc[-1]), self.Revision_SIG]
            return self.LIST

    pre_list = []

    for j in stocklist:
        stock = cal()
        stock.setter(j)
        stock.get_rsi()
        stock.get_boll()
        stock_info = [str(j)] + stock.get_result()
        pre_list.append(stock_info)

    df_result1 = pd.DataFrame(pre_list, columns=['Symbol', 'BOLL', 'B_WD', 'B_R', 'BR_DAYS', 'B_MMT', 'RSI', 'SIGNAL'])
    df_result2 = df_result1.sort_values('SIGNAL', ascending=False)
    df_result3 = df_result2.iloc[0:15]
    html_table = df_result3.to_html(index=False)
    return html_table

@app.route('/coin')
def coin():
    return "Coming Soon!"

if __name__ == '__main__':
    app.run(debug=True)