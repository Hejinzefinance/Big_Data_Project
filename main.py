from Backtest import Backtest
import pandas as pd

close_data = pd.read_excel('close_data.xlsx')
close_data.set_index('date', inplace=True)
code_name = pd.read_excel('codes_name.xlsx', squeeze=1)
my_weights = pd.read_excel('weights.xlsx', sheet_name='Sheet4')
my_weights.set_index('date', inplace=True)

close_data = close_data.iloc[:300]
my_weights = my_weights.iloc[:300]

backtest = Backtest(close_data, code_name)
backtest.getWeights(my_weights)
backtest.runBackTest()
a = 1
