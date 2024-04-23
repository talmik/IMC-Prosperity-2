import json
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any
import numpy as np
import pandas as pd

# if you trade gift baskets and don't trade the roses, chocs and strawberries you make  Final Profit / Loss: 4,313


class Logger:
    def __init__(self) -> None:
        self.logs = ""

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]], conversions: int, trader_data: str) -> None:
        print(json.dumps([
            self.compress_state(state),
            self.compress_orders(orders),
            conversions,
            trader_data,
            self.logs,
        ], cls=ProsperityEncoder, separators=(",", ":")))

        self.logs = ""

    def compress_state(self, state: TradingState) -> list[Any]:
        return [
            state.timestamp,
            state.traderData,
            self.compress_listings(state.listings),
            self.compress_order_depths(state.order_depths),
            self.compress_trades(state.own_trades),
            self.compress_trades(state.market_trades),
            state.position,
            self.compress_observations(state.observations),
        ]

    def compress_listings(self, listings: dict[Symbol, Listing]) -> list[list[Any]]:
        compressed = []
        for listing in listings.values():
            compressed.append([listing["symbol"], listing["product"], listing["denomination"]])

        return compressed

    def compress_order_depths(self, order_depths: dict[Symbol, OrderDepth]) -> dict[Symbol, list[Any]]:
        compressed = {}
        for symbol, order_depth in order_depths.items():
            compressed[symbol] = [order_depth.buy_orders, order_depth.sell_orders]

        return compressed

    def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
        compressed = []
        for arr in trades.values():
            for trade in arr:
                compressed.append([
                    trade.symbol,
                    trade.price,
                    trade.quantity,
                    trade.buyer,
                    trade.seller,
                    trade.timestamp,
                ])

        return compressed

    def compress_observations(self, observations: Observation) -> list[Any]:
        conversion_observations = {}
        for product, observation in observations.conversionObservations.items():
            conversion_observations[product] = [
                observation.bidPrice,
                observation.askPrice,
                observation.transportFees,
                observation.exportTariff,
                observation.importTariff,
                observation.sunlight,
                observation.humidity,
            ]

        return [observations.plainValueObservations, conversion_observations]

    def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
        compressed = []
        for arr in orders.values():
            for order in arr:
                compressed.append([order.symbol, order.price, order.quantity])

        return compressed

logger = Logger()

class Trader:
    POSITION_LIMIT = {'AMETHYSTS':20, 'STARFRUIT': 20, 'ORCHIDS': 100, 'GIFT_BASKET': 60, 'STRAWBERRIES': 350, 'CHOCOLATE': 250, 'ROSES': 60}
    ourPosition = {'AMETHYSTS':0, 'STARFRUIT': 0, 'ORCHIDS': 0, 'GIFT_BASKET': 0, 'STRAWBERRIES': 0, 'CHOCOLATE': 0, 'ROSES': 0}
    bestBids =  {'AMETHYSTS':[0,0], 'STARFRUIT': [0,0], 'ORCHIDS': [0,0], 'GIFT_BASKET': [0,0], 'STRAWBERRIES': [0,0], 'CHOCOLATE': [0,0], 'ROSES': [0,0]}
    bestAsks = {'AMETHYSTS':[0,0], 'STARFRUIT': [0,0], 'ORCHIDS': [0,0], 'GIFT_BASKET': [0,0], 'STRAWBERRIES': [0,0], 'CHOCOLATE': [0,0], 'ROSES': [0,0]}
    products = ['AMETHYSTS', 'STARFRUIT', 'ORCHIDS', 'GIFT_BASKET', 'STRAWBERRIES', 'CHOCOLATE', 'ROSES']
    beta = 40 # I have tried 100, 10

    chocolatePrice =[]
    rosesPrice = []
    strawberriesPrice = []
    gift_basketPrice = []
    NAV = []
    c_multiplier = 4 #4
    s_multiplier = 6 #6
    r_multiplier = 1 #1
    b_multiplier = 1
     
    def buyAmount_withLimits(self, buyAmount, position, limit):
        # buyAmount is always positive
        return min(limit-position, buyAmount)

    def sellAmount_withLimits(self, sellAmount, position, limit):
        # sellAmount if positive
        return max(-limit-position, -sellAmount)
    
    def findBasketAmount(self, dataCorrelation): # this only activates when NAV and baskets drift apart
        n = 0.5 -dataCorrelation
        quantity = int(4*n)+1
        return quantity

    def findCorrelation(self,list1, list2):
        d = {'list 1':list1, 'list 2': list2}
        data = pd.DataFrame(d)
        dataCorrelation = data.corr()['list 1']['list 2']
        return dataCorrelation

    def run(self, state: TradingState):
        result ={}
        conversions = 0
        trader_data = ""
        logger.print("traderData: " + state.traderData)
        logger.print("Observations: " + str(state.observations))

        for key, val in state.position.items():
            self.ourPosition[key] = val

        for product in self.products:
            if len(state.order_depths[product].sell_orders) != 0: 
                self.bestAsks[product] = list(state.order_depths[product].sell_orders.items())[0]
            if len(state.order_depths[product].buy_orders) != 0:
                self.bestBids[product] = list(state.order_depths[product].buy_orders.items())[0]
                if product == 'CHOCOLATE':
                    self.chocolatePrice.append(self.bestBids['CHOCOLATE'][0])
                if product == 'ROSES':
                    self.rosesPrice.append(self.bestBids['ROSES'][0])
                if product == 'STRAWBERRIES':
                    self.strawberriesPrice.append(self.bestBids['STRAWBERRIES'][0])
                if product == 'GIFT_BASKET':
                    self.gift_basketPrice.append(self.bestBids['GIFT_BASKET'][0])
        self.NAV.append(4*self.chocolatePrice[-1]+6*self.strawberriesPrice[-1]+self.rosesPrice[-1])

        if state.timestamp >= self.beta*100:
            dataCorrelation = self.findCorrelation(self.NAV[-self.beta:], self.gift_basketPrice[-self.beta:])
        else: 
            dataCorrelation = 0.6 # I do not wish to trigger pairs trading when the dataCorrelation is not low enough to indicate drift, nor high enough to indicate they are paired together again

        for product in state.order_depths: 
            orders: List[Order] = []
            if product == 'AMETHYSTS':
                if self.bestAsks[product][0] < 10000:
                    amount = self.buyAmount_withLimits(self.bestAsks[product][1], self.ourPosition[product], self.POSITION_LIMIT[product])
                    orders.append(Order(product, self.bestAsks[product][0], amount))
                if self.bestBids[product][0] > 10000:
                    orders.append(Order(product, self.bestBids[product][0], self.sellAmount_withLimits(self.bestBids[product][1],self.ourPosition[product] ,self.POSITION_LIMIT[product]))) 
            
            if product == 'GIFT_BASKET':
                if dataCorrelation < 0.5:
                    if self.NAV[-1] > self.gift_basketPrice[-1]:
                        # buy basket, sell component
                        basket_buy_amount = self.b_multiplier*self.findBasketAmount(dataCorrelation) # without any consideration of limits
                        basket_buy_amount_withLimits = self.buyAmount_withLimits(basket_buy_amount, self.ourPosition['GIFT_BASKET'], self.POSITION_LIMIT['GIFT_BASKET'])
                        orders.append(Order('GIFT_BASKET', self.bestAsks['GIFT_BASKET'][0], basket_buy_amount_withLimits))  
                    elif self.NAV[-1] < self.gift_basketPrice[-1]:
                        # sell basket, buy components
                        basket_sell_amount = self.findBasketAmount(dataCorrelation)
                        basket_sell_amount_withLimits = self.sellAmount_withLimits(basket_sell_amount, self.ourPosition['GIFT_BASKET'], self.POSITION_LIMIT['GIFT_BASKET'])
                        orders.append(Order('GIFT_BASKET', self.bestBids['GIFT_BASKET'][0], basket_sell_amount_withLimits))
                elif dataCorrelation > 0.8:
                    # CLOSE POSITIONS
                    if self.ourPosition['GIFT_BASKET'] > 0:
                        orders.append(Order('GIFT_BASKET', self.bestBids['GIFT_BASKET'][0], -self.ourPosition['GIFT_BASKET']))
                    if self.ourPosition['GIFT_BASKET'] < 0:
                        orders.append(Order('GIFT_BASKET', self.bestAsks['GIFT_BASKET'][0], -self.ourPosition['GIFT_BASKET']))
            if product == 'CHOCOLATE':
                #c_correlation = self.findCorrelation(self.chocolatePrice[-self.beta:], self.gift_basketPrice[-self.beta:])
                basket_buy_amount = self.findBasketAmount(dataCorrelation)
                if dataCorrelation < 0.5:
                    amount = self.c_multiplier*basket_buy_amount
                    if self.NAV[-1] > self.gift_basketPrice[-1]:
                        c_amount_withLimits = self.sellAmount_withLimits(amount, self.ourPosition['CHOCOLATE'], self.POSITION_LIMIT['CHOCOLATE'])
                        orders.append(Order('CHOCOLATE', self.bestBids['CHOCOLATE'][0], c_amount_withLimits))
                    elif self.NAV[-1] < self.gift_basketPrice[-1]:
                        c_amount_withLimits = self.buyAmount_withLimits(amount, self.ourPosition['CHOCOLATE'], self.POSITION_LIMIT['CHOCOLATE'])
                        orders.append(Order('CHOCOLATE', self.bestAsks['CHOCOLATE'][0], c_amount_withLimits))
                if dataCorrelation > 0.8 and self.ourPosition['GIFT_BASKET'] >0:
                    orders.append(Order('CHOCOLATE', self.bestBids['CHOCOLATE'][0], -self.ourPosition['CHOCOLATE']))
                if dataCorrelation > 0.8 and self.ourPosition['GIFT_BASKET'] < 0:
                    orders.append(Order('CHOCOLATE', self.bestAsks['CHOCOLATE'][0], -self.ourPosition['CHOCOLATE']))
            if product == 'STRAWBERRIES':
                #s_correlation = self.findCorrelation(self.strawberriesPrice[-self.beta:], self.gift_basketPrice[-self.beta:])
                basket_buy_amount = self.findBasketAmount(dataCorrelation)
                if dataCorrelation < 0.5:
                    amount = self.s_multiplier*basket_buy_amount
                    if self.NAV[-1] > self.gift_basketPrice[-1]:
                        s_amount_withLimits = self.sellAmount_withLimits(amount, self.ourPosition['STRAWBERRIES'], self.POSITION_LIMIT['STRAWBERRIES'])
                        orders.append(Order('STRAWBERRIES', self.bestBids['STRAWBERRIES'][0], s_amount_withLimits))
                    elif self.NAV[-1] < self.gift_basketPrice[-1]:
                        s_amount_withLimits = self.buyAmount_withLimits(amount, self.ourPosition['STRAWBERRIES'], self.POSITION_LIMIT['STRAWBERRIES'])
                        orders.append(Order('STRAWBERRIES', self.bestAsks['STRAWBERRIES'][0], s_amount_withLimits))
                if dataCorrelation > 0.8 and self.ourPosition['GIFT_BASKET'] >0:
                    orders.append(Order('STRAWBERRIES', self.bestBids['STRAWBERRIES'][0], -self.ourPosition['STRAWBERRIES']))
                if dataCorrelation > 0.8 and self.ourPosition['GIFT_BASKET'] < 0:
                    orders.append(Order('STRAWBERRIES', self.bestAsks['STRAWBERRIES'][0], -self.ourPosition['STRAWBERRIES']))
            if product == 'ROSES':
                #r_correlation = self.findCorrelation(self.rosesPrice[-self.beta:], self.gift_basketPrice[-self.beta:])
                basket_buy_amount = self.findBasketAmount(dataCorrelation)
                if dataCorrelation < 0.5:
                    amount = self.r_multiplier*basket_buy_amount
                    if self.NAV[-1] > self.gift_basketPrice[-1]:
                        r_amount_withLimits = self.sellAmount_withLimits(amount, self.ourPosition['ROSES'], self.POSITION_LIMIT['ROSES'])
                        orders.appendd(Order('ROSES', self.bestBids['ROSES'][0], r_amount_withLimits))
                    elif self.NAV[-1] < self.gift_basketPrice[-1]:
                        r_amount_withLimits = self.buyAmount_withLimits(amount, self.ourPosition['ROSES'], self.POSITION_LIMIT['ROSES'])
                        orders.append(Order('ROSES', self.bestAsks['ROSES'][0], r_amount_withLimits))
                if dataCorrelation > 0.8 and self.ourPosition['GIFT_BASKET'] >0:
                    orders.append(Order('ROSES', self.bestBids['ROSES'][0], -self.ourPosition["ROSES"]))
                if dataCorrelation > 0.8 and self.ourPosition['GIFT_BASKET'] <0:
                    orders.append(Order('ROSES', self.bestAsks['ROSES'][0], -self.ourPosition['ROSES']))
            result[product] = orders
        traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        
        conversions = 1

        logger.flush(state, result, conversions, trader_data)
        return result, conversions, trader_data