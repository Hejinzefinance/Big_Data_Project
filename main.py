from Backtest import Backtest
close_data = pd.read_excel('close_data.xlsx')
code_name = pd.read_excel('codes_name.xlsx')
backtest = Backtest(close_data, code_name)
a=1