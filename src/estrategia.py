import backtrader as bt
import random

# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('periodShortSMA', 5),
        ('periodLongSMA', 30),
        ('rsi_period', 10),
        ('rsi_upper', 70),
        ('rsi_lower', 30),
        ('maxOrders', 20),
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
        self.bb = bt.indicators.BollingerBands()

        self.generateBuySignal1()
        self.generateBuySignal2()
        self.generateBuySignal3()

        self.generateSellSignal1()
        self.generateSellSignal2()
        self.generateSellSignal3()

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.orders = []
        self.buyprice = None
        self.buycomm = None

    # Cross method
    def generateBuySignal1(self):
        self.buySignal1 = bt.indicators.CrossUp(self.shortSMA, self.longSMA)

    def generateSellSignal1(self):
        self.sellSignal1 = bt.indicators.CrossDown(self.shortSMA, self.longSMA)        
    
    # RSI
    def generateBuySignal2(self):
        self.buySignal2 = self.rsi < self.params.rsi_lower
    
    def generateSellSignal2(self):
        self.sellSignal2 = self.rsi > self.params.rsi_upper

    # Bollinger bands
    def generateBuySignal3(self):
        self.buySignal3 = self.data.close < self.bb.bot

    def generateSellSignal3(self):
        self.sellSignal3 = self.data.close > self.bb.top

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

        # Check si se llego al maximo numero de ordenes concurrentes permitido. Si es asi cancelar todas.
        if len(self.orders) >= self.params.maxOrders:
            for order in self.orders:
                self.cancel(order)
                self.orders.remove(order)
            return

        # Evaluan indicadores de compra
        if self.cash >= self.dataclose[0] and self.buySignal1[0] or self.buySignal2[0]:
            self.log(f'shortSMA: {self.shortSMA[0]}, longSMA: {self.longSMA[0]}')
            # BUY
            self.log('BUY CREATE, %.2f' % self.dataclose[0])
            # Calcular el size de la orden.
            size = int(self.cash / (self.dataclose[0]*1.01) * ((100 - self.rsi[0])/100))
            self.log(f'size: {size}')
            # Añadir orden a ordenes abiertas
            self.orders.append(self.buy(size=size))

        # Si tenemos activos en la cartera
        if self.position: 
            # Evaluar indicadores de venta
            
            if self.sellSignal1[0] or self.sellSignal3[0]:
                self.log(f'sellsignal1: {self.sellSignal1[0]}, sellsignal2: {self.sellSignal2[0]}, sellsignal3: {self.sellSignal3[0]}')
                # SELL
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.log((self.rsi[0])/100)
                size = self.position.size * ((self.rsi[0])/100)

                # Keep track of the created order to avoid a 2nd order
                self.orders.append(self.sell(size=int(size)))

    def notify_cashvalue(self, cash, value):
        self.value = value
        self.cash = cash
        print(f'cash: {cash}, value: {value}')

    def stop(self):
        self.log(f'Position: {self.position}')