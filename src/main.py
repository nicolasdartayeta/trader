from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
from estrategia import (TestStrategy)

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '../data/JPM.csv')

    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(2020, 1, 1),
        # Do not pass values before this date
        todate=datetime.datetime(2024, 1, 1),
        # Do not pass values after this date
        reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.001)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    initValue = cerebro.broker.getvalue()
    # Run over everything
    cerebro.run()
    
    finalValue = cerebro.broker.getvalue()

    # finalPosition = cerebro.broker.getposition(data)

    # Por si quedamos comprados en algun instrumento
    # if (finalPosition):
        # finalValue += + finalPosition.price * finalPosition.size

    # Print out the final result
    print('Final Portfolio Value: %.2f' % finalValue)
    profit = (finalValue / initValue - 1)*100
    print(f'Profit: {round(profit, 2)}%')
    cerebro.plot()