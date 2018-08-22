# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 19:18:12 2017

@author: ricky_xu
"""

from __future__ import print_function

from abc import ABCMeta, abstractmethod

try:
    import Queue as queue
except ImportError:
    import queue


class Strategy(object):
    """
    Strategy is an abstract base class providing an interface for all subsequent (inherited) strategy handling objects.
    A Strategy object encapsulates all calculation on market data that generate advisory signals to a Portfolio object.
    """
    __metaclass = ABCMeta

    @abstractmethod
    def calculate_signals(self):
        raise NotImplementedError("Should implement calculate_signals()")
