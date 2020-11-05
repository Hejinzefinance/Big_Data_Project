import pandas as pd
class Account:
    def __init__(self, initial_cash, stamp_tax_rate,codes_all):
        self.cash_amount = initial_cash
        self.tax_rate = stamp_tax_rate
        self.curr_data = pd.DataFrame(index = codes_all, columns = ['price', 'quantity', 'amount'])
        self.exp_quantity = pd.Series(index = codes_all)
        self.next_price = pd.Series(index = codes_all)

    def getExpQuantity(self, exp_quantity):
        self.exp_quantity = exp_quantity

    def getNextPrice(self,next_price):
        self.next_price = next_price

    def executeOrder(self):
        pass

    def calStampCost(self):
        pass