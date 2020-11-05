#%% Import modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime as dt
from Account import Account
#%% Class Definition
class Backtest:
    def __init__(self, price_mat_data, code_name):
        # 重要成员
        self.price_mat_data = price_mat_data
        self.code_name = pd.Series(index = price_mat_data.columns, value = code_name)
        self.initConstParas()
        self.reset()
        # 超参数
        self.initial_cash = 1e8
        self.stamp_tax_rate = 0.001

    def settings(self,initial_cash,stamp_tax_rate):
        self.initial_cash = initial_cash
        self.stamp_tax_rate = stamp_tax_rate

    def initConstParas(self):
        self.codes_all = self.price_mat_data.columns
        self.times_all = self.price_mat_data.index
        self.start_time = self.times_all[0]
        self.end_time = self.times_all[-1]

    def reset(self):
        self.curr_time = self.start_time
        self.curr_exp_return = pd.Series(index = self.codes_all)
        self.pnl_intervals = pd.Series(index = self.times_all[1:])
        self.stamp_cost = pd.Series(index = self.times_all[1:])
        self.exp_returns = pd.DataFrame(index = self.times_all[1:], columns = self.codes_all)
        self.initAccount()

    def initAccount(self):
        self.account = Account(self.initial_cash, self.stamp_tax_rate, self.codes_all)