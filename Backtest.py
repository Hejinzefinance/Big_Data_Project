#%% Import modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime as dt
from Account import Account
import os
#%% Class Definition
class Backtest:
    def __init__(self, price_mat_data, code_name):
        # 重要成员
        self.price_mat_data = price_mat_data
        self.code_name = pd.Series(data=code_name.values, index=price_mat_data.columns)
        self.initConstParas()
        self.initAccount()

    def setAccount(self, initial_cash, stamp_tax_rate):
        self.account.settings(initial_cash, stamp_tax_rate)

    def runBackTest(self):
        for idx, curr_time in enumerate(self.times_all):
            self.curr_time = curr_time
            if self.curr_time == self.start_time:
                pass
            else:
                self.account.recordPnL(self.curr_time, self.price_mat_data.loc[self.curr_time])
            if self.curr_time == self.end_time:
                self.finishStrategy()
            curr_pos_info = self.account.getCurrPos(self.curr_time)
            target_weight = self.normalize(self.target_weights.loc[curr_time])
            if curr_pos_info['nav'] <= 0:
                self.bankCruptsy()
            curr_orders = self.generateOrders(curr_pos_info, target_weight)
            self.account.executeOrder(curr_orders, self.price_mat_data.loc[self.curr_time])
            if idx % 30 == 0:
                print(self.curr_time)

    def generateOrders(self, curr_pos_info, target_weight):
        curr_weight = curr_pos_info['trading_securities'].amount / curr_pos_info['nav']
        diff_weight = target_weight - curr_weight
        signs = diff_weight.map(self.sign)
        deducted_value = (diff_weight.loc[signs == -1] * curr_pos_info['nav'])
        deducted_quant = self.quantFloor(
            deducted_value / self.price_mat_data.loc[self.curr_time, signs == -1])  # 多卖点，克服印花税的削弱作用
        left_money = curr_pos_info['cash'] - (
            self.price_mat_data.loc[self.curr_time, signs == -1].T) @ deducted_quant * (1 - self.account.tax_rate)
        increased_value = self.normalize(diff_weight.loc[signs == 1]) * left_money
        increased_quant = self.quantFloor(
            increased_value / self.price_mat_data.loc[self.curr_time, signs == 1])  # 少买点，怕钱不够
        trading_quant = pd.concat([deducted_quant, increased_quant], axis=0).sort_index()
        return trading_quant

    def bankCruptsy(self):
        print('破产了！！！')

    def finishStrategy(self):
        self.max_drawback_ratios = self.calMD(self.account.nav_after_trading)
        self.calMetrics()

    def identifyTrend(self, width):
        moving_average_center = self.account.nav_after_trading.rolling(width, center=True, min_periods=1).mean()
        self.trends = moving_average_center.diff().fillna(1).map(self.sign)

    def calMetrics(self):
        self.strategy_metrics = dict()
        self.strategy_metrics['AR'] = np.power(
            self.account.nav_after_trading.iloc[-1] / self.account.nav_after_trading.iloc[0],
            self.account.nav_after_trading.shape[0] / 252)
        self.strategy_metrics['AV'] = self.account.nav_after_trading.pct_change().dropna().std() * np.sqrt(252)
        self.strategy_metrics['SR'] = self.strategy_metrics['AR'] / self.strategy_metrics['AV']
        self.strategy_metrics['MD'] = self.max_drawback_ratios.max()
        self.strategy_metrics['CMR'] = self.strategy_metrics['AR'] / self.strategy_metrics['MD']
        win_lose = self.account.nav_after_trading.diff().dropna().map(self.sign)
        self.strategy_metrics['WR'] = (win_lose == 1).sum() / win_lose.shape[0]

    def plot_nav(self, png_path='figures/', file_name='performance.png', trend_width=5):
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        self.identifyTrend(trend_width)
        fig = plt.figure(figsize=(12, 6))
        ax1 = fig.add_axes([0.05, 0.05, 0.9, 0.9])
        line1 = ax1.plot(self.account.nav_after_trading)
        stem_container = ax1.stem(self.account.nav_after_trading.loc[self.trends == 1].index,
                                  self.account.nav_after_trading.loc[self.trends == 1],
                                  markerfmt='.', linefmt='pink', basefmt='w')
        plt.setp(stem_container, 'markersize', 0)
        stem_container = ax1.stem(self.account.nav_after_trading.loc[self.trends == -1].index,
                                  self.account.nav_after_trading.loc[self.trends == -1],
                                  markerfmt='.', linefmt='#4AB7FF', basefmt='w')
        plt.setp(stem_container, 'markersize', 0)
        ax1.set_ylim(0, 1.5 * self.account.nav_after_trading.max())
        ax2 = ax1.twinx()
        stem_container = ax2.stem(self.max_drawback_ratios.index, -self.max_drawback_ratios, linefmt='red',
                                  markerfmt='r-')
        ax2.set_ylim(-self.max_drawback_ratios.max() * 4, 0)
        plt.setp(stem_container, 'markersize', 0)
        ax1.set_title('净值曲线&回撤比率-趋势窗口长度:{0:d}'.format(trend_width))
        plt.legend(line1 + stem_container[1], ('net_asset_value', 'drawdown_ratio'), loc=2)
        plt.tight_layout()
        plt.savefig(png_path + file_name, dpi=300, figsize=(12, 6))
        if file_name is not None:
            if not os.path.exists('figures'):
                os.mkdir('figures')
            plt.savefig(png_path + file_name, dpi=300)

    def getWeights(self, weights):
        self.target_weights = weights

    @classmethod
    def calMD(cls, nav_series):
        nav_max_series = cls.calHistoryMax(nav_series)
        drawdown = nav_max_series - nav_series
        max_drawdown_ratios = drawdown / nav_max_series
        return max_drawdown_ratios

    @staticmethod
    def calHistoryMax(series_data):
        max_value = -float('inf')
        hist_max_data = series_data.copy()
        for curr_time in series_data.index:
            new_value = series_data.loc[curr_time]
            if new_value > max_value:
                max_value = new_value
            hist_max_data.loc[curr_time] = max_value
        return hist_max_data

    @staticmethod
    def sign(element):
        if element >= 0:
            return 1
        else:
            return -1

    def initConstParas(self):
        self.codes_all = self.price_mat_data.columns
        self.times_all = self.price_mat_data.index
        self.start_time = self.times_all[0]
        self.end_time = self.times_all[-1]

    def reset(self):
        self.curr_time = self.start_time
        self.max_drawback_ratio = None
        self.strategy_metrics = dict()
        self.account.reset()

    def initAccount(self):
        self.account = Account(self.codes_all, self.start_time)

    @staticmethod
    def normalize(vector):
        return vector / sum(vector)

    @staticmethod
    def quantFloor(quant):
        return np.floor(quant / 100) * 100

    @staticmethod
    def quantCeil(quant):
        return np.ceil(quant / 100) * 100