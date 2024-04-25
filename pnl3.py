import numpy as np
import pandas as pd
from matplotlib import pyplot

#CHOCOLATE, STRAWBERRIES, ROSES, GIFT_BASKET

df = pd.read_csv('trades_round_3_day_2_wn.csv', sep = ';')

time = list(df['timestamp'])
traders = list(df['buyer'])+list(df['seller'])
traders = set(traders)
traders = list(traders)


def buyer(name, timestamp, symbol):
    # transactions in which you act as a buyer
    global df 
    d = df[df['timestamp']<=timestamp]
    listBuyer = d[d['buyer']== name]
    listBuyer = listBuyer[listBuyer['symbol'] == symbol]
    price = list(listBuyer['price'])
    quantity = list(listBuyer['quantity'])
    spend = [price[i]*quantity[i] for i in range(0,len(price))]
    return sum(spend)


def seller(name,timestamp, symbol):
    global df
    d = df[df['timestamp']<=timestamp]
    listSeller = d[d['seller'] == name]
    listSeller = listSeller[listSeller['symbol'] == symbol]
    price = list(listSeller['price'])
    quantity = list(listSeller['quantity'])
    earn = [price[i]*quantity[i] for i in range(0,len(price))]
    return sum(earn)

def profit(name, timestamp, symbol):
    return seller(name, timestamp, symbol)-buyer(name, timestamp, symbol)

def generateGraph(symbol, traders):
    for name in traders:
        profitOverTime = [profit(name, i, symbol) for i in time]
        pyplot.plot(time, profitOverTime, label = str(name))
    pyplot.legend()
    pyplot.show()

def buyerG(name, timestamp):
    # transactions in which you act as a buyer
    global df 
    d = df[df['timestamp']<=timestamp]
    listBuyer = d[d['buyer']== name]
    price = list(listBuyer['price'])
    quantity = list(listBuyer['quantity'])
    spend = [price[i]*quantity[i] for i in range(0,len(price))]
    return sum(spend)


def sellerG(name,timestamp):
    global df
    d = df[df['timestamp']<=timestamp]
    listSeller = d[d['seller'] == name]
    price = list(listSeller['price'])
    quantity = list(listSeller['quantity'])
    earn = [price[i]*quantity[i] for i in range(0,len(price))]
    return sum(earn)

def profitG(name, timestamp):
    return sellerG(name, timestamp)-buyerG(name, timestamp)

def generateGraphG(traders):
    for name in traders:
        profitOverTime = [profitG(name, i) for i in time]
        pyplot.plot(time, profitOverTime, label = str(name))
    pyplot.legend()
    pyplot.show()

generateGraphG(traders)


#generateGraph('GIFT_BASKET', traders)
#Vladimir very positive on chcolate, roses, straberries, most negative on baskets
# were Rhianna and V implementing a pairs trading strat?


# copy Vladimir's strat
