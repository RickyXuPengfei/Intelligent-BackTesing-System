# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 20:59:55 2017

@author: ricky_xu
"""

from __future__ import print_function

import datetime
import os
import os.path
from abc import ABCMeta, abstractmethod

import numpy as np
import pandas as pd

from event import MarketEvent


class DataHandler(object):
    """
    DataHandler is an abstract class that provides an interface for all data handlers
    """

    @abstractmethod
    def get_latest_bar(self, symbol):
        """
        return the last bar

        :param symbol: string; the ticker symbol

        :return:Series; the last bar
        """
        raise NotImplementedError("should implement get_latest_bar()")

    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        """
        return the latest bars

        :param symbol: string; the ticker symbol

        :param N: int; the number of the bars

        :return: a list of Series; the lasted bars
        """
        raise NotImplementedError("should implement get_latest_bars()")

    @abstractmethod
    def get_latest_bar_datetime(self, symbol):
        """
        return datetime object of latest bar

        :param symbol: string; the ticker symbol

        :return: datetime; datetime of latest bar
        """
        raise NotImplementedError("should implement get_latest_bar_datetime()")

    @abstractmethod
    def get_latest_bar_value(self, symbol, val_type):
        """
        return value of the latest bar

        :param symbol: string; the ticker symbol

        :param val_type: string, one of column names

        :return: type of value; return value of the latest bar
        """
        raise NotImplementedError("should implement get_latest_bar_value()")

    @abstractmethod
    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        returns the values of the latest bars

        :param symbol: string; the ticker symbol

        :param val_type: string, one of column names

        :param N: int; the number of the bars

        :return: a list of val_type; a list of value of the lasted bars
        """
        raise NotImplementedError("should implement get_latest_bars_values()")

    @abstractmethod
    def update_bars(self):
        """
        read each one from bar generator, then generate MarketEvent
        """
        raise NotImplementedError("should implement update_bars()")


class HistoricCSVDataHandler(DataHandler):
    def __init__(self, events, csv_dir, symbol_list):
        """

        :param events: Queue; the Events Queue

        :param csv_dir: string; the path of csv data

        :param symbol_list: list; a list of symbol strings

        :param symbol_data: dict; key: symbol value: A generator that iterates over the rows of the frame (each one is a tuple [0]: index(datetime); [1]:values)

        :param latest_symbol_data: dict; key: string; value: a list of rows from symbol_data rows

        :param continue_backtest: boolean; determine if updating new bar
        """
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True

        self._open_convert_csv_files()

    def _open_convert_csv_files(self):
        """
        read csv data into DataFrame, and generate symbol_data
        """
        comb_index = None
        for s in self.symbol_list:
            self.symbol_data[s] = pd.io.parsers.read_csv(os.path.join(self.csv_dir, '%s.csv' % s),
                                                         header=0, index_col=0, parse_dates=True,
                                                         names=[
                                                             'datetime', 'open', 'high', 'low', 'close', 'volume',
                                                             'adj_close'])

            if comb_index is None:  # 联合index给dataframe下一个数据
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)

            self.latest_symbol_data[s] = []

        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index, method='pad').iterrows()

    def _get_new_bar(self, symbol):
        """
        illustrate the iteration of symbol_data

        :param symbol: string; the ticker symbol

        """
        for b in self.symbol_data[symbol]:
            yield b

    def get_latest_bar(self, symbol):
        """
        return the latest bar from latest_symbol_data by selecting the symbol

        :param symbol: string; the ticker symbol

        :return: Series; the last bar
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set")
            raise
        else:
            return bars_list[-1]

    def get_latest_bars(self, symbol, N=1):
        """
        returns a list of bars from latest_symbol_data by selecting the symbol

        :param symbol: string; the ticker symbol

        :param int; the number of the bars

        :return: a list of Series; the lasted bars
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set")
            raise
        else:
            return bars_list[-N:]

    def get_latest_bar_datetime(self, symbol):
        """
        returns datetime object of latest bar

        :param symbol: string; the ticker symbol

        :return: datetime; datetime object of latest bar : datetime is the index of latest bar
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical date set")
            raise
        else:
            return bars_list[-1][0]

    def get_latest_bar_value(self, symbol, val_type):
        """

        return value of the latest bar[1] by selecting val_type

        :param symbol: string; the ticker symbol

        :param val_type: string, one of column names

        :return: type of value; return value of the latest bar
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set")
            raise
        else:
            return getattr(bars_list[-1][1], val_type)

    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        returns the values of the latest bars

        :param symbol: string; the ticker symbol

        :param val_type: string, one of column names

        :param N: int; the number of the bars

        :return: a list of val_type; a list of value of the lasted bars
        """
        try:
            bars_list = self.get_latest_bars(symbol, N)
        except KeyError:
            print("The symbol is not available in the historical data set")
            raise
        else:
            return np.array([getattr(b[1], val_type) for b in bars_list])

    def update_bars(self):
        """
        read each row of symbol_data into latest_symbol_data
        then, generate MarketEvent
        it's used in backtest module

        """
        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s))
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent())
