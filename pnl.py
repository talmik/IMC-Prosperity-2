import numpy as np
import pandas as pd
from matplotlib import pyplot

#amethyst, starfruit

df = pd.read_csv('trades_round_1_day_-2_wn.csv', sep = ';')


# given a person how to pull their pnl over time
# if you buy something at a certain price, then -price*quantity, if you sell something at a certain price then +price*quantity
# and your positions will be kept in a dict. At the end of the sesh we liquidate according to best bid and best ask at that time

time = list(df['timestamp'])

remyBuys = df[df['buyer']=='Remy']
remyBuys = remyBuys[remyBuys['symbol']=='STARFRUIT']
remyBuysTime = list(remyBuys[remyBuys['buyer']=='Remy']['timestamp'])
remyBuysPrice = list(remyBuys[remyBuys['buyer']=='Remy']['price'])
remySells = df[df['seller']=='Remy']
remySells = remySells[remySells['symbol'] == 'STARFRUIT']
remySellsTime = list(remySells[remySells['seller']=='Remy']['timestamp'])
remySellsPrice = list(remySells[remySells['seller']=='Remy']['price'])

pyplot.scatter(remyBuysTime, remyBuysPrice, label = 'as a buyer')
pyplot.scatter(remySellsTime, remySellsPrice, label = 'seller')
pyplot.legend()
pyplot.show()


def buyer(name, timestamp):
    # transactions in which you act as a buyer
    global df 
    d = df[df['timestamp']<=timestamp]
    listBuyer = d[d['buyer']== name]
    price = list(listBuyer['price'])
    quantity = list(listBuyer['quantity'])
    spend = [price[i]*quantity[i] for i in range(0,len(price))]
    return sum(spend)


def seller(name,timestamp):
    global df
    d = df[df['timestamp']<=timestamp]
    listSeller = d[d['seller'] == name]
    price = list(listSeller['price'])
    quantity = list(listSeller['quantity'])
    earn = [price[i]*quantity[i] for i in range(0,len(price))]
    return sum(earn)

def profit(name, timestamp):
    return seller(name, timestamp)-buyer(name, timestamp)

productList = ['AMETHYSTS', 'STARFRUIT']

def makePositionDict(name):
    return {'AMETHYSTS':0, 'STARFRUIT':0}

def position(name, timestamp):
    global df
    global productList
    dictionary = makePositionDict(name)
    d = df[df['timestamp']<=timestamp]
    seller = d[d['seller'] == name]
    print(seller)
    buyer = d[d['buyer']== name]
    for item in productList:
        itemSellerDF = seller[seller['symbol']==item]
        print(itemSellerDF)
        itemSellerDFQuantity = list(itemSellerDF['quantity'])
        print(itemSellerDFQuantity)
        itemBuyerDF = buyer[buyer['symbol']==item]
        itemBuyerDFQuantity = list(itemBuyerDF['quantity'])
        p = sum(itemBuyerDFQuantity) - sum(itemSellerDFQuantity)
        dictionary[item] = p
    return dictionary

def liquidate(positionDict):
    count = 0
    for item in list(positionDict.keys()):
        count += liquidateSymbol(item, positionDict[item])
    return count

def liquidateSymbol(symbol, quantity):
    if symbol =='AMETHYSTS':
        price = 9998 
    elif symbol == 'STARFRUIT':
        price = 5041
    return quantity*price



"""

#Valentina, negative
profitPerTimeValentina = [profit('Valentina', i) for i in time]
pyplot.plot(time, profitPerTimeValentina, label = 'Valentina')

#Vinnie, heavily positive, 800 000

profitPerTimeVinnie = [profit('Vinnie', i) for i in time]
pyplot.plot(time, profitPerTimeVinnie, label = 'Vinnie')

#Amelia, negative, consistent losses. up to -1.25 mil
#print(profitPerTimeAmelia)
profitPerTimeAmelia = [profit('Amelia', i) for i in time]
pyplot.plot(time, profitPerTimeAmelia, label = 'Amelia')


#Remy, has like 1.2 million profit by the end of the day. 
profitPerTimeRemy = [profit('Remy', i) for i in time]
#print(profitPerTimeRemy)
pyplot.plot(time, profitPerTimeRemy, label = 'Remy')

#vladimir

profitPerTimeVladimir = [profit('Vladimir', i) for i in time]
pyplot.plot(time, profitPerTimeVladimir, label = 'Vladimir')

#Rhianna, pretty positive

profitPerTimeRhianna = [profit('Rhianna', i) for i in time]
#print(profitPerTimeRhianna)
pyplot.plot(time, profitPerTimeRhianna, label = 'Rhianna')

#Ruby
profitPerTimeRuby = [profit('Ruby', i) for i in time]
#print(profitPerTimeRhianna)
pyplot.plot(time, profitPerTimeRuby, label = 'Ruby')
"""

#Vivian
"""
profitPerTimeVivian = [profit('Vivian', i) for i in time]
p = position('Vivian', 999600)
#print(profitPerTimeRhianna)
pyplot.plot(time, profitPerTimeVivian, label = 'Vivian')

# colin
profitPerTimeColin = [profit('Colin', i) for i in time]
p = position('Colin', 999600)
pyplot.plot(time, profitPerTimeColin, label = 'Colin')

#Celeste

profitPerTimeCeleste = [profit('Celeste', i) for i in time]
p = position('Celeste', 999600)
pyplot.plot(time, profitPerTimeCeleste, label = 'Celeste')

#Carlos
profitPerTimeCarlos = [profit('Carlos', i) for i in time]
p = position('Carlos', 999600)
pyplot.plot(time, profitPerTimeCarlos, label = 'Carlos')

#Camilia
profitPerTimeCamilia = [profit('Camilia', i) for i in time]
p = position('Camilia', 999600)
pyplot.plot(time, profitPerTimeCamilia, label = 'Camilia')
"""
"""pyplot.legend()
pyplot.show()"""

# copy Remy, very positive

# or accept every offer Valentina makes

# you can only see counterparty after trade is done

# we could see if there are trends. ie. if the bot keeps buying, then just hop on and do the same

