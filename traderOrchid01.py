import json
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any

class Logger:
    def __init__(self) -> None:
        self.logs = ""
        self.max_log_length = 3750

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]], conversions: int, trader_data: str) -> None:
        base_length = len(self.to_json([
            self.compress_state(state, ""),
            self.compress_orders(orders),
            conversions,
            "",
            "",
        ]))

        # We truncate state.traderData, trader_data, and self.logs to the same max. length to fit the log limit
        max_item_length = (self.max_log_length - base_length) // 3

        print(self.to_json([
            self.compress_state(state, self.truncate(state.traderData, max_item_length)),
            self.compress_orders(orders),
            conversions,
            self.truncate(trader_data, max_item_length),
            self.truncate(self.logs, max_item_length),
        ]))

        self.logs = ""

    def compress_state(self, state: TradingState, trader_data: str) -> list[Any]:
        return [
            state.timestamp,
            trader_data,
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

    def to_json(self, value: Any) -> str:
        return json.dumps(value, cls=ProsperityEncoder, separators=(",", ":"))

    def truncate(self, value: str, max_length: int) -> str:
        if len(value) <= max_length:
            return value

        return value[:max_length - 3] + "..."

logger = Logger()

class Trader:
    def run(self, state: TradingState) -> tuple[dict[Symbol, list[Order]], int, str]:
        result = {}
        conversions = 0
        trader_data = ""
        # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        bservations = state.observations.conversionObservations["ORCHIDS"]


    
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            ourPosition = state.position.get(product,0)
            if len(order_depth.sell_orders) != 0: 
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            if len(order_depth.buy_orders) !=0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            if product == 'ORCHIDS':
                fair = 982.2107803421892 + 8.21202841333334*bservations.transportFees + 1.7782800613333334*bservations.exportTariff + 14.63011926*bservations.importTariff + 0.007313904166666666*bservations.sunlight+ 1.4945271666666666*bservations.humidity
                fair = int(fair)
                if best_bid > fair:
                    logger.print('SELL', str(-best_bid_amount)+'x', best_bid)
                    orders.append(Order(product, best_bid, -best_bid_amount))
                if best_ask < fair-8:
                    orders.append(Order(product, best_ask, -best_ask_amount))
                    logger.print('BUY', str(-best_ask_amount)+'x',best_ask)
            elif product == 'AMETHYSTS':
                if best_ask < 10000:
                    logger.print('BUY', str(20-ourPosition) + 'x', best_ask)
                    orders.append(Order(product, best_ask, (20-ourPosition)))
                if best_bid > 10000:
                    logger.print('SELL', str(-(20+ourPosition))+'x', best_bid)
                    orders.append(Order(product, best_bid, -(20+ourPosition)))

        result[product] = orders
    
    
        traderData = "SAMPLE" 
        conversions = 1

        logger.flush(state, result, conversions, trader_data)
        return result, conversions, trader_data