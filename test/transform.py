"""
TRANSFORMACIÓN DE VARIABLES
"""

from src.python.util.stats import data_transformer
from src.python.util.basic import load_arrow
from src.python.util.stats import normalizer
from src.python.util.stats import sma
import matplotlib.pyplot as plt
import statsmodels.api as sm
import seaborn as sns
import pandas as pd
import numpy as np


interval = '30m'
file = 'data/02 clean'
name = f'BTCUSDT_{interval}'
data = load_arrow(file, name)
transf = data_transformer(data)
df = transf["data"]

plt.style.use('ggplot')
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=['#4C72B0'])

value = df["Volume_Qty"].rolling(window=100).mean()
sample = value.sample(n=10000, random_state=50).sort_index()
_, _ = plt.subplots(figsize=(8, 4))
plt.plot(sample)
plt.title('Normalización móvil del volumen (Muestreo 1%)')
plt.xlabel('Índice')
plt.ylabel('Norm Volume')
plt.show()


# Correlograma de transformaciones logarítmicas
_df = pd.DataFrame()
_df['Time'] = df['Time']
_df['Open'] = df['Open']
_df['High'] = df['High']
_df['Low'] = df['Low']
_df['Close'] = df['Close']
_df['Open_Log'] = df['Open_Log']
_df['High_Log'] = df['High_Log']
_df['Low_Log'] = df['Low_Log']
_df['Close_Log'] = df['Close_Log']
_df['HL2_Log'] = df['HL2_Log']
_df['Volume_Log'] = df['Volume_Log']
_df['Volume_Qty'] = df['Volume_Qty']
_df['Taker_Prop'] = df['Taker_Prop']
_df['Volume_Trade'] = df['Volume_Trade']
corrmat = _df.corr()
mask = np.triu(np.ones_like(corrmat, dtype=bool))
plt.figure(figsize=(8, 6))
sns.heatmap(corrmat, mask=mask, cmap='coolwarm', linewidths=.5)
plt.title('Matriz de Coorrelación')
plt.show()


# Correlograma de transformaciones normales
_df = pd.DataFrame()
_df['Time'] = df['Time']
_df['Open'] = df['Open']
_df['High'] = df['High']
_df['Low'] = df['Low']
_df['Close'] = df['Close']
_df['Open_Norm'] = df['Open_Norm']
_df['High_Norm'] = df['High_Norm']
_df['Low_Norm'] = df['Low_Norm']
_df['Close_Norm'] = df['Close_Norm']
_df['HL2_Norm'] = df['HL2_Norm']
_df['Volume_Norm'] = df['Volume_Norm']
_df['Filled_MA'] = df['Filled_MA']
_df['Volume_Qty'] = df['Volume_Qty']
_df['Taker_Prop'] = df['Taker_Prop']
_df['Volume_Trade'] = df['Volume_Trade']
corrmat = _df.corr()
mask = np.triu(np.ones_like(corrmat, dtype=bool))
plt.figure(figsize=(8, 6))
sns.heatmap(corrmat, mask=mask, cmap='coolwarm', linewidths=.5)
plt.title('Matriz de Coorrelación')
plt.show()
