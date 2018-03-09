# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 20:23:05 2017

@author: ricky_xu
"""

from __future__ import print_function

"""
there are four types of events which allow communication
between different components via event queue

"""

class Event(object):
    """
    Event provide the interface
    """

    pass

class MarketEvent(Event):
    """
    MarketEvent occurs when DataHandler object receive new market data.
    """
    def __init__(self):
        """
        :param type: int; define the MarketEvent
        """
        self.type='MARKET'
        
class SignalEvent(Event):
    """
    MarketEvent object can trigger Strategy objcet to calculate signal.
    In the process, SignalEvent can be generatd and is put into event queue.
    """
    def __init__(self,strategy_id,symbol,datetime,signal_type,strength):
        """
        :param type: 'SIGNAL' define the SignalEvent

        :param strategy_id: int; the identifier for the strategy to generate the signal

        :param symbol: string; the ticker symbol

        :param datetime: Datetime; the timetample when the signal generates

        :param signal_type: String; 'LONG' or 'SHORT'

        :param strength: float; quantity at the profile level.
        """
        self.type = 'SIGNAL'
        self.strategy_id = strategy_id
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type
        self.strength = strength

class OrderEvent(Event):
    """
    When profile object receive SignalEvent, then it can update signal and generates new OrderEvent objcet
    And, it can be put into Event Queue.
    """
    def __init__(self,symbol,order_type,quantity,direction):
        """

        :param symbol: string; the ticker symbol

        :param order_type: string; ’MKT’ or ’LMT’ for Market or Limit.

        :param quantity: int; no-negative value for quantity

        :param direction: string; ’BUY’ or ’SELL’ for long or short. (more complexe than SignalEvent.signal_type, mkt_quantity and current quantity should be taken into consideration)
        """
        self.type='ORDER'
        self.symbol=symbol
        self.order_type=order_type
        self.quantity=quantity
        self.direction=direction

    def print_order(self):
        """
        :return: print the values of OrderEvent
        """
        print (
                "Order: Symbol=%s, Type=%s,Quantity=%s,Direction=%s" %
                (self.symbol,self.order_type,self.quantity,self.direction)
                )
        
class FillEvent(Event):
    """
    Execution_handler receives OrderEvent, it runs execute_order to generate FillEvent that describes the cost ot the transaction
    Then, profile can update holdings_from_fill,positions_from_fill(event)
    """
    def __init__(self,timeindex,symbol,exchange,quantity,direction,fill_cost,commission=None):
        """
        :param type: string; 'FILL' define FillEvent

        :param timeindex: datetime; datetime.datetime.utcnow()

        :param symbol: string; the ticker symbol

        :param exchange: string; e.g 'ARCA'  the exchange where the order was filled

        :param quantity: int; no-negative value for quantity

        :param direction: string; ’BUY’ or ’SELL’ for long or short.

        :param fill_cost: the holding cost (without commission)

        :param commission: 手续费
        """
        self.type='FILL'
        self.timeindex=timeindex
        self.symbol=symbol
        self.exchange=exchange
        self.quantity=quantity
        self.direction=direction
        self.fill_cost=fill_cost #持有资金
        
        if commission is None:
            self.commission=self.calculate_ib_commission()
        else:
            self.commission=commission
            
    def calculate_ib_commission(self):
        """

        :return: float; the fees of trading
        """

        full_cost=1.3
        if self.quantity<=500:
            full_cost=max(1.3,0.013*self.quantity)
        else:
            full_cost=max(1.3,0.008*self.quantity)
        return full_cost
    
        