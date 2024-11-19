import backtrader as bt

# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('periodShortSMA', 10),
        ('periodLongSMA', 60),
        ('rsi_period', 14),
        ('rsi_upper', 70),
        ('rsi_lower', 30),
        ('maxOrders', 10),
        ('exitbars', 5),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # Indicadores
        self.shortSMA = bt.indicators.SMA(self.data.close, period=self.params.periodShortSMA)
        self.longSMA = bt.indicators.SMA(self.data.close, period=self.params.periodLongSMA)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)

        self.generateBuySignal1()
        self.generateBuySignal2()
        self.buySignal3 = True

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.orders = []
        self.buyprice = None
        self.buycomm = None

    # Cross method
    def generateBuySignal1(self):
        self.buySignal1 = bt.indicators.CrossUp(self.shortSMA, self.longSMA)
    
    def generateBuySignal2(self):
        self.buySignal2 = bt.indicators.CrossUp(self.rsi, self.params.rsi_lower)
    
    def generateSellSignal2(self):
        self.sellSignal2 = bt.indicators.CrossDown(self.rsi, self.params.rsi_upper)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.orders.remove(order)

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if len(self.orders) >= self.params.maxOrders:
            return

        # Not yet ... we MIGHT BUY if ...
        if self.buySignal1[0] and self.buySignal2[0]:
            self.log(f'shortSMA: {self.shortSMA[0]}, longSMA: {self.longSMA[0]}')
            # BUY, BUY, BUY!!! (with default parameters)
            self.log('BUY CREATE, %.2f' % self.dataclose[0])

            # Keep track of the created order to avoid a 2nd order
            self.orders.append(self.buy())
        if self.position: 
            # Already in the market ... we might sell
            if len(self) >= (self.bar_executed + self.params.exitbars):
                # SELL
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.orders.append(self.sell())