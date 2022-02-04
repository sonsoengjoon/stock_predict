import pandas as pd
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
import Analyzer
import Backtrader as bt

startcash = 1000000
cerebro = bt.Cerebro()

mk = Analyzer.MarketDB()
df = mk.get_daily_price()

df
