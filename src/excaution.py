# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 21:11:38 2017

@author: ricky_xu
"""

from __future__ import print_function
from abc import ABCMeta,abstractmethod 
import datetime
try:
    import Queue as queue 
except ImportError:
    import queue

from event import FillEvent,OrderEvent

class ExecutionHandler(object):
    """
    Interface provided to generate FillEvent.
    """
    __metaclass__=ABCMeta
    
    @abstractmethod
    def execute_order(self,event):
        raise NotImplementedError("should implement execute_order()")
        
class SimulatedExecutionHandler(ExecutionHandler):
    """
    converts all order objects into their equivalent fill objects automatically
    """
    def __init__(self,events):
        """

        :param events: The Queue of Event objects.
        """
        self.events=events
        
    def execute_order(self,event):
        """
        Simply converts Order objects into Fill objects naively

        :param event: Event; OrderEvent.
        """
        if event.type=='ORDER':
            fill_event=FillEvent(
                    datetime.datetime.utcnow(),event.symbol,
                    'ARCA',event.quantity,event.direction,None)
            self.events.put(fill_event)
            
            