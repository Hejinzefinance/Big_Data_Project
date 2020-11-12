import pandas as pd
import numpy as np
from datetime import datetime as dt, timedelta as td


class Account:
    def __init__(self, codes_all, start_time):
        # 超参数默认值
        self.initial_cash = 1e8
        self.tax_rate = 0.001
        # 临时变量
        self.curr_time = start_time
        self.last_time = start_time - td(1)
        self.last_price = None
        self.new_price = None
        # 重要变量
        self.codes_all = codes_all
        self.start_time = start_time
        self.cash_amount = pd.Series(self.initial_cash, index=[self.last_time])
        self.before_trading_amount = pd.DataFrame(data=np.zeros((1, self.codes_all.shape[0])),
                                                  index=[self.start_time], columns=self.codes_all)
        self.after_trading_amount = pd.DataFrame(index=[self.start_time], columns=self.codes_all)
        self.holding_quant = pd.DataFrame(index=[self.last_time, self.start_time], columns=self.codes_all)
        self.holding_quant.loc[self.last_time] = np.zeros((1, self.codes_all.shape[0]))
        self.pnl_log = pd.DataFrame(index=[self.start_time], columns=self.codes_all)
        self.pnl_series = pd.Series(index=[self.start_time])
        self.stamp_cost = pd.Series(index=[self.start_time])
        self.nav_before_trading = pd.Series(self.initial_cash, index=[self.start_time])
        self.nav_after_trading = pd.Series(index=[self.start_time])

    # 超参数设定
    def settings(self, initial_cash, stamp_tax_rate):
        self.initial_cash = initial_cash
        self.tax_rate = stamp_tax_rate

    # 重置函数
    def reset(self):
        self.curr_time = self.start_time
        self.last_time = self.start_time - dt(1)
        self.last_price = None
        self.new_price = None
        self.before_trading_amount = pd.DataFrame(data=np.zeros((1, self.codes_all.shape[0])),
                                                  index=[self.start_time], columns=self.codes_all)
        self.after_trading_amount = pd.DataFrame(index=[self.start_time], columns=self.codes_all)
        self.holding_quant = pd.DataFrame(index=[self.last_time, self.start_time], columns=self.codes_all)
        self.holding_quant.loc[self.last_time] = np.zeros((1, self.codes_all.shape[0]))
        self.pnl_log = pd.DataFrame(index=[self.start_time], columns=self.codes_all)
        self.pnl_series = pd.Series(index=[self.start_time])
        self.stamp_cost = pd.Series(index=[self.start_time])
        self.cash_amount = pd.Series(self.initial_cash, index=[self.last_time])

    def executeOrder(self, curr_orders, prices):
        self.new_price = prices
        self.holding_quant.loc[self.curr_time] = self.holding_quant.loc[self.last_time] + curr_orders
        self.stamp_cost.loc[self.curr_time] = -prices.T @ curr_orders.map(self.negamere) * self.tax_rate
        self.cash_amount.loc[self.curr_time] = self.cash_amount.loc[self.last_time] - prices.T @ curr_orders - \
                                               self.stamp_cost.loc[self.curr_time]
        self.after_trading_amount.loc[self.curr_time] = prices.T * self.holding_quant.loc[self.curr_time]
        self.nav_after_trading.loc[self.curr_time] = self.after_trading_amount.loc[self.curr_time].sum() + \
                                                     self.cash_amount.loc[self.curr_time]

    def calStampCost(self):
        pass

    def getCurrPos(self, curr_time):
        output = dict()
        curr_quant = self.holding_quant.loc[self.last_time].T
        curr_amount = self.before_trading_amount.loc[curr_time].T
        output['trading_securities'] = pd.concat([curr_quant, curr_amount], axis=1)
        output['trading_securities'].columns = ['quant', 'amount']
        output['cash'] = self.cash_amount.loc[self.last_time]
        output['nav'] = self.nav_before_trading.loc[curr_time]
        return output

    def calLastTime(self, curr_time):
        curr_idx = self.holding_quant.index.get_loc(curr_time)
        return self.holding_quant.index[curr_idx - 1]

    @staticmethod
    def orthomere(element):
        return max(element, 0)

    @staticmethod
    def negamere(element):
        return min(element, 0)

    def recordPnL(self, new_time, new_prices):
        self.last_time = self.curr_time
        self.curr_time = new_time
        self.last_price = self.new_price
        self.new_price = new_prices
        self.before_trading_amount.loc[self.curr_time] = new_prices * self.holding_quant.loc[self.last_time]
        self.nav_before_trading.loc[self.curr_time] = self.before_trading_amount.loc[self.curr_time].sum() + \
                                                      self.cash_amount.loc[self.last_time]
        self.pnl_log.loc[self.curr_time] = self.before_trading_amount.loc[self.curr_time] - \
                                           self.after_trading_amount.loc[self.last_time]
        self.pnl_series.loc[self.curr_time] = self.pnl_log.loc[self.curr_time].sum()
