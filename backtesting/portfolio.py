# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 16:51:08 2017

@author: ricky_xu
"""

from __future__ import print_function

try:
    import Queue as queue
except ImportError:
    import queue
import pandas as pd

from event import OrderEvent
from performance import create_sharpe_ratio, create_drawdowns


class Portfolio(object):
    """
    Portfolio can handle the positions and market value of all instruments at a resolution of a Bar object.
    """

    def __init__(self, bars, events, start_date, initial_capital=100000):
        """
        :param bars: DataHandler; DataHandler object with current data.

        :param events: Queue; event queue.

        :param start_date: datetime; timestamp of start date.

        :param initial_capital: float; initial capital.

        :param symbol_list: list; a list of symbol strings

        :param all_positions: list of dict; historical list of a dict(k: datetime and symbol strings; v:datetime and positions of all symbols)

        :param current_position: dict; current position for last market bar updated.

        :param all_holdings: dict; historical list of all symbol holdings.

        :param current_holdings: dict; the most up to date dict of all symbol holdings values.

        :param equity_curve: DataFrame; record performance of the strategy
        """

        self.bars = bars
        self.events = events
        self.symbol_list = self.bars.symbol_list
        self.start_date = start_date
        self.initial_capital = initial_capital
        self.all_positions = self.construct_all_positions()
        self.current_positions = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        self.all_holdings = self.construct_all_holdings()
        self.current_holdings = self.construct_current_holdings()
        self.equity_curve = None

    def construct_all_positions(self):
        """
        Construct a list of dict containing datetime and each position of each symbol.
        :return: list; a list of dict containing datetime and each position of each symbol.
        """
        d = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        d['datetime'] = self.start_date
        return [d]

    def construct_all_holdings(self):
        """

        Construct a list of dict containing datetime and each holdins(cash, commisson, total) of each symbol.

        :return: list; a list of dict containing datetime and each holdins(cash, commisson, total) of each symbol.
        """
        d = dict((k, v) for k, v in [(s, 0.0) for s in self.symbol_list])
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commisson'] = 0.0
        d['total'] = self.initial_capital

        return [d]

    def construct_current_holdings(self):
        """
        Construct a dict containing the holdings(cash, commission, total) of all symbols and its datetime is current datetime

        :return:a dict containing the holdings(cash, commission, total) of all symbols
        """
        d = dict((k, v) for k, v in [(s, 0.0) for s in self.symbol_list])
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        return d

    # append this set of current positions to the all_positions list
    def update_timeindex(self, event):
        """
        append this set of current positions to the all_positions list

        :param event: Event; it can be used in backtest and backtest can trigger it when its type is MARKET.


        """
        latest_datetime = self.bars.get_latest_bar_datetime(self.symbol_list[0])

        dp = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        dp['datetime'] = latest_datetime

        for s in self.symbol_list:
            dp[s] = self.current_positions[s]

        self.all_positions.append(dp)

        dh = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        dh['datetime'] = latest_datetime
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['total']

        for s in self.symbol_list:
            market_value = self.current_positions[s] * self.bars.get_latest_bar_value(s, 'adj_close')
            dh[s] = market_value
            dh['total'] += market_value

        self.all_holdings.append(dh)

    # FillEvent buy or  sell==> update current_positions
    def update_positions_from_fill(self, fill):
        """
        update the current positions depend the direction of FillEvent.

        :param fill: FillEvent; it can be used in backtest.

        """
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        self.current_positions[fill.symbol] += fill_dir * fill.quantity

    def update_holdings_from_fill(self, fill):
        """
        update current holdings depend on FillEvent.

        :param fill: FillEvent; it can be used in backtest.

        """
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1
        fill_cost = self.bars.get_latest_bar_value(fill.symbol, "adj_close")
        cost = fill_dir * fill_cost * fill.quantity
        self.current_holdings[fill.symbol] += cost
        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= (cost + fill.commission)

    def update_fill(self, event):
        """
        encapsulate update_holdings_from_fill() and update_positions_from_fill().

        :param event: FillEvent;

        """
        if event.type == 'FILL':
            self.update_holdings_from_fill(event)
            self.update_positions_from_fill(event)

    def generate_navie_order(self, signal):
        """
        Create OrderEvent using SignalEvent.

        :param signal: SignalEvent;  it's created in strategy.calculate_signals()

        :return: OrderEvent; use the attributes of SignalEvent to generate OrderEvent.
        """
        order = None

        symbol = signal.symbol
        direction = signal.signal_type
        strength = signal.strength

        mkt_quantity = 100
        cur_quantity = self.current_positions[symbol]
        order_type = 'MKT'

        if direction == 'LONG' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'BUY')
        if direction == 'SHORT' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'SELL')
        if direction == 'EXIT' and cur_quantity > 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'SELL')
        if direction == 'EXIT' and cur_quantity < 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'BUY')
        return order

    # 根据SIFGNAL添加order到event queue
    def update_signal(self, event):
        """
        It can be used in backtest. put OrderEvent into EventQueue.

        :param event: Event; do put operation depend on SignalEvent.

        """
        if event.type == 'SIGNAL':
            order_event = self.generate_navie_order(event)
            self.events.put(order_event)

    def create_equity_curve_dataframe(self):
        """
        It is the part of output_performance of backtest. It generate DataFrame(index: datetime, columns: returns equity_curve )

        """

        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0 + curve['returns']).cumprod()
        self.equity_curve = curve

    def output_summary_stats(self):
        """
        Calulate states(total_return, sharpe_ratio, max_drawdown, max_duration).

        :return: list; summary data.
        """
        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']

        sharpe_ratio = create_sharpe_ratio(returns, periods=252 * 60 * 6.5)
        drawdown, max_dd, max_duration = create_drawdowns(pnl)
        self.equity_curve['drawdown'] = drawdown

        stats = [("Total Return", "%0.2f%%" % ((total_return - 1.0) * 100.0)),
                 ("Sharpe Ratio", "%0.2f%%" % sharpe_ratio),
                 ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0)),
                 ("Drawdown Duration", "%d" % max_duration)]
        self.equity_curve.to_csv('equity.csv')
        return stats
