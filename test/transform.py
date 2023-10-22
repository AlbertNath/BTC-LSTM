"""
TRANSFORMACIÓN DE VARIABLES
"""

from src.python.util.basic import load_arrow
from src.python.util.basic import save_arrow
from src.python.util.stats import normalizer
from src.python.util.stats import sma
import matplotlib.pyplot as plt
import statsmodels.api as sm
import seaborn as sns
import pandas as pd
import numpy as np
import random


def scaler(data):
    min_val = data.min()
    max_val = data.max()
    data_scaled = (data - min_val) / (max_val - min_val)
    return data_scaled


def data_transformer(data, n=2880, mindate="2018-01-01", scalet=60000):
    df = pd.DataFrame()
    hl2 = (data['High'] + data['Low']) / 2
    df['Time'] = data["Time"]
    df['Open'] = data["Open"]
    df['High'] = data["High"]
    df['Low'] = data["Low"]
    df['Close'] = data["Close"]
    ####### LOGARITMO DE VARIABLES ######
    df['Open_Log'] = np.log(data["Open"])
    df['High_Log'] = np.log(data["High"])
    df['Low_Log'] = np.log(data["Low"])
    df['Close_Log'] = np.log(data["Close"])
    df['HL2_Log'] = np.log(hl2)
    df['Volume_Log'] = np.log(5 + data["Volume"])
    ####### NORMALIZACIÓN DE PRECIOS ######
    price_normalizer = normalizer(hl2, n)
    norm = price_normalizer["norm"]
    df['Open_Norm'] = norm(data["Open"])
    df['High_Norm'] = norm(data["High"])
    df['Low_Norm'] = norm(data["Low"])
    df['Close_Norm'] = norm(data["Close"])
    df['HL2_Norm'] = norm(hl2)
    ####### NORMALIZACIÓN DE VOLUMEN ######
    volume_normalizer = normalizer(
        data["Volume"], n)  # normalizador de precios
    df['Volume_Norm'] = volume_normalizer["norm"](data["Volume"])
    ####### TRANSFORMACIÓN DE VARIABLES ######
    df['Filled_MA'] = sma(data["Filled"], 2*n-2)
    df['Volume_Qty'] = (data["Volume"] /
                        (data["Volume"] + data["VolumeUSDT"] / data["Close"]))
    df['Taker_Prop'] = (data["TakerVolumeUSDT"] /
                        (data["Volume"] + data["TakerVolumeUSDT"]))
    df['Volume_Trade'] = data["Volume"] / data["Trades"]
    mintime = pd.Timestamp(mindate).timestamp() * 1000 / scalet
    minindex = max(2 * n - 2, (data['Time'] >= mintime).idxmax())
    time = df['Time']
    df = scaler(df.iloc[minindex:])
    df['Time'] = time
    return {
        'data': df,
        'price_normalizer': price_normalizer,
        'volume_normalizer': volume_normalizer
    }


interval = '30m'
file = 'data/02 clean'
name = f'BTCUSDT_{interval}'
data = load_arrow(file, name)
transf = data_transformer(data)
df = transf["data"]

plt.style.use('ggplot')
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=['#4C72B0'])

# data_time = [pd.Timestamp(int(x*60), unit="s") for x in df['Time']]
#### Desviación estandar media del precio ####
std = data["Close"].rolling(window=1000).std()
_, _ = plt.subplots(figsize=(8, 4))
plt.plot(std)
plt.title('Desviación estandar media del precio')
plt.xlabel('Índice')
plt.ylabel('Variación del precio')
plt.show()

#### Desviación estandar media del volumen ####
std = data["Volume"].rolling(window=1000).std()
_, _ = plt.subplots(figsize=(8, 4))
plt.plot(std)
plt.title('Desviación estandar media del volumen')
plt.xlabel('Índice')
plt.ylabel('Variación del volumen')
plt.show()

#### Log Close ####
value = df["Close_Log"].rolling(window=100).mean()
sample = value.sample(n=10000, random_state=42).sort_index()
_, _ = plt.subplots(figsize=(8, 4))
plt.plot(sample)
plt.title('Logaritmo del precio de cierre (Muestreo 1%)')
plt.xlabel('Índice')
plt.ylabel('Log Close')
plt.show()

#### Log Volume ####
value = df["Volume_Log"].rolling(window=100).mean()
sample = value.sample(n=10000, random_state=42).sort_index()
_, _ = plt.subplots(figsize=(8, 4))
plt.plot(sample)
plt.title('Logaritmo del volumen (Muestreo 1%)')
plt.xlabel('Índice')
plt.ylabel('Log Volume')
plt.show()

#### Log Close ####
value = df["Close_Norm"].rolling(window=100).mean()
sample = value.sample(n=10000, random_state=42).sort_index()
_, _ = plt.subplots(figsize=(8, 4))
plt.plot(sample)
plt.title('Normalización móvil del precio de cierre (Muestreo 1%)')
plt.xlabel('Índice')
plt.ylabel('Norm Close')
plt.show()

#### Log Volume ####
value = df["Volume_Norm"].rolling(window=100).mean()
sample = value.sample(n=10000, random_state=42).sort_index()
_, _ = plt.subplots(figsize=(8, 4))
plt.plot(sample)
plt.title('Normalización móvil del volumen (Muestreo 1%)')
plt.xlabel('Índice')
plt.ylabel('Norm Volume')
plt.show()


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
