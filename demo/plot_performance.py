import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_csv('equity.csv')
data = data.set_index(['datetime'])

fig = plt.figure(figsize=(13, 7))
fig.patch.set_facecolor('white')

ax1 = fig.add_subplot(311, ylabel='Portfolio value, %')
data['equity_curve'].plot(ax=ax1, color='blue', lw=2.)
plt.grid(True)

ax2 = fig.add_subplot(312, ylabel='Portfolio returns, %')
data['returns'].plot(ax=ax2, color='black', lw=2.0)
plt.grid(True)

ax3 = fig.add_subplot(313, ylabel='Drawdowns, %')
data['drawdown'].plot(ax=ax3, color='red', lw=2.0)
plt.grid(True)
plt.tight_layout()

plt.show()
