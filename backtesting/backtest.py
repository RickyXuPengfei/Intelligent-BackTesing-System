# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 09:15:01 2017

@author: ricky_xu
"""

from __future__ import print_function

import pprint

try:
    import Queue as queue
except ImportError:
    import queue
import time


class Backtest(object):
    def __init__(self, csv_dir, symbol_list, initial_capital, heartbeat, start_date, data_handler, execution_handler,
                 portfolio, strategy):
        """
        :param csv_dir: string; head root of CSV data.

        :param symbol_list: list; a list of symbol strings.

        :param initial_capital: float; The starting capital for the portfolio

        :param heartbeat: float; Backtest "heartbeat" in seconds

        :param start_date: datetime; start datetime of the strategy.

        :param data_handler: DataHandler; HistoricCSVDataHandler

        :param execution_handler: ExecutionHandler; SimulatedExecutionHandler

        :param portfolio: Portfolio; keep track the data to update current holdings and positions.

        :param strategy:Strategy; use to calculate the signal and generate SignalEvent.
        """

        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        self.initial_capital = initial_capital
        self.heartbeat = heartbeat
        self.start_date = start_date

        self.data_handler_cls = data_handler
        self.execution_handler_cls = execution_handler
        self.portfolio_cls = portfolio
        self.strategy_cls = strategy

        self.events = queue.Queue()

        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strats = 1

        self._generate_trading_instances()

    # create Datahandler,strategy,portfolio,execution
    def _generate_trading_instances(self):
        """
        Generates the trading instance objects from
        their class types.
        """

        print("creating DataHandler,Strategy,Portfolio and ExecutionHandler")
        self.data_handler = self.data_handler_cls(self.events, self.csv_dir, self.symbol_list)
        self.strategy = self.strategy_cls(self.data_handler, self.events)
        self.portfolio = self.portfolio_cls(self.data_handler, self.events, self.start_date, self.initial_capital)
        self.execution_handler = self.execution_handler_cls(self.events)

    def _run_backtest(self):
        """
        Executes the backtest.
        """

        i = 0
        while True:
            i += 1
            print(i)
            if self.data_handler.continue_backtest == True:
                self.data_handler.update_bars()
            else:
                break

            while True:
                try:
                    event = self.events.get(False)
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if event.type == 'MARKET':
                            self.strategy.calculate_signals(event)
                            self.portfolio.update_timeindex(event)
                        elif event.type == 'SIGNAL':
                            self.signals += 1
                            self.portfolio.update_signal(event)
                        elif event.type == 'ORDER':
                            self.orders += 1
                            self.execution_handler.execute_order(event)
                        elif event.type == 'FILL':
                            self.fills += 1
                            self.portfolio.update_fill(event)
            time.sleep(self.heartbeat)

    def _output_performance(self):
        """
        Outputs the strategy performance from the backtest.
        """

        self.portfolio.create_equity_curve_dataframe()

        print("creating summary stats...")
        stats = self.portfolio.output_summary_stats()

        print("creating equity curve")
        print(self.portfolio.equity_curve.tail(10))
        pprint.pprint(stats)

        print("Signal: %s" % self.signals)
        print("Orders: %s" % self.orders)
        print("Fills: %s" % self.fills)

    def simulate_trading(self):
        """
        Simulates the backtest and outputs portfolio performance.
        """
        self._run_backtest()
        self._output_performance()
