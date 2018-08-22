# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 16:21:04 2017

@author: ricky_xu
"""

from __future__ import print_function

import numpy as np
import pandas as pd


def create_sharpe_ratio(returns, periods=252):
    """
    Create the Sharpe ratio for the strategy, based on a
    benchmark of zero (i.e. no risk-free rate information).

    :param returns: Series; period percentage returns.
    :param periods: int; Daily (252), Hourly (252*6.5), Minutely(252*6.5*60) etc.
    :return: float; Sharpe ratio
    """
    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns)


def create_drawdowns(pnl):
    """

    Calculate the largest peak-to-trough drawdown of the PnL curve as well as the duration of the drawdown.

    :param pnl: Series; period percentage returns.
    :return: Series; drawdown.  float; max of drawdown.   int; max of drawdown duration.
    """

    hwm = [0]

    # create the drawdown and duration series
    idx = pnl.index
    drawdown = pd.Series(index=idx)
    duration = pd.Series(index=idx)

    for t in range(1, len(idx)):
        hwm.append(max(hwm[t - 1], pnl[t]))
        drawdown[t] = (hwm[t] - pnl[t])
        duration[t] = (0 if drawdown[t] == 0 else duration[t - 1] + 1)
    return drawdown, drawdown.max(), duration.max()
