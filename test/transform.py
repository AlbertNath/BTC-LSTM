
from src.python.util.basic import load_arrow
from src.python.util.basic import save_arrow
from src.python.util.stats import histplot
from src.python.util.stats import sample
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import seaborn as sns



interval = '30m'
file = 'data/02 clean'
name = f'BTCUSDT_{interval}'
data = load_arrow(file, name)
data


def sma(src, n=1):
    if (n > 1):
        return src.rolling(window=n).mean()
    return src


def sta(src, n=1):
    if (n > 1):
        return sma((src-sma(src, n=n))**2, n - 1) ** 0.5

def lag(src, n=0):
    if n == 0:
        return src
    if n > 0:
        return src[:-n]
    return src[-n:]



src = data['Volume']
lag(src, 2)

len(src)