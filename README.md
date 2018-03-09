![] (https://github.com/RickyXuPengfei/Intelligent-BackTesing-System/blob/master/images/logo1.png)
Intelligent BackTesting System
==============================

It is currently in development - if you find a bug, please submit an issue.

Read the docs here: **[Modules](docs/html/index.html)**.

What is Intelligent BackTesting System?
-----------

The system is a flexible backtesting framework for Python used to test quantitative
trading strategies. **Backtesting** is the process of testing a strategy over a given 
data set. This framework allows you to easily create strategies. The important thing is that it's an **Event-Driven** framework. So it allows the illusion of real-time response handling because the code is continually being looped and events checked for. 

The goal: to save **quants** from re-inventing the wheel and let them focus on the 
important part of the job - strategy development. It is coded in **Python** and joins a vibrant and rich ecosystem for data analysis. It utilize lots of python library(Numpy, Pandas) that python users get used to. 


Features
---------

* **Code Reuse**
> An event-driven backtester, by design, can be used for both historical backtesting and live trading with minimal switch-out of components. This is 	not true of vectorised backtesters where all data must be available at once 	to carry out statistical analysis.

* **Lookahead Bias**
>    With an event-driven backtester there is no lookahead bias as market data receipt is treated as an "event" that must be acted upon. Thus it is possible to "drip feed" an event-driven backtester with market data, replicating how an order management and portfolio system would behave.

* **Realism**
> Event-driven backtesters allow significant customisation over how orders are executed and transaction costs are incurred. It is straightforward to handle basic market and limit orders, as well as market-on-open (MOO) and market-on-close (MOC), since a custom exchange handler can be constructed.

## Dependencies：

* Python 3.x/2.7 
* Numpy
* Pandas
* Matplotlib

## Architecture:
![Architecture] (https://github.com/RickyXuPengfei/Intelligent-BackTesing-System/blob/master/images/Architecture.png)


Getting Started
---------------

### DataFormat

 All all data store in datas/. And each csv file should fit the format.
 
	 | datetime     | open    |  high   | low   | close | volume   | adj_close
     | Aug 07, 2017 | 3212.78 |  3397.68|3180.89|3378.94|1482280000|3378.94
     | Aug 06, 2017 | 3257.61 |  3293.29|3155.6 |3213.94|1105030000|3213.94
    
    
### Import Modules
```
from __future__ import print_function
import datetime
import numpy as np

from strategy import Strategy
from event import SignalEvent
from backtest import Backtest
from data import HistoricCSVDataHandler
from excaution import SimulatedExecutionHandler
from portfolio import Portfolio
```
Users can directly use the  modules in src/. And details of each modules are descripted **[here](docs/html/index.html)**.


### Strategy
In this part, we use ***Moving Average Crossover technical system***  to write this strategy.

Now we turn to the creation of the MovingAverageCrossStrategy. The strategy requires both the bars DataHandler, the events Event Queue and the lookback periods for the simple moving averages that are going to be employed within the strategy. I’ve chosen 100 and 400 as the "short" and "long" lookback periods for this strategy.

The final attribute, bought, is used to tell the Strategy when the backtest is actually "in the market". Entry signals are only generated if this is "OUT" and exit signals are only ever generated if this is "LONG" or "SHORT":

```
class MovingAverageCrossStrategy(Strategy):

    def __init__(self, bars, events, short_window=10, long_window=30):
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.short_window = short_window
        self.long_window = long_window
        self.bought = self._calculate_initial_bought()


    def _calculate_initial_bought(self):
        """
        Adds keys to the bought dictionary for all symbols and sets them to ’OUT’.
        """
        bought = {s:'OUT' for s in self.symbol_list}
        return  bought
```

The core of the strategy is the calculate_signals method. The code is in [***mac***](demo/mac.py).

### Visualize Performance
After running the strategy, we can get data called ***equity.csv***. Then running [***plot_performace***](demo/plot_performance.py) can get the performance.
![performance] (https://github.com/RickyXuPengfei/Intelligent-BackTesing-System/blob/master/images/performance)


Discussing
----------
- email: ricky.xu@connect.polyu.hk



