from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import kpss

import pandas as pd
import numpy as np
import warnings
import random

# Función que calcula los estadísticos para un diagrama de caja


def boxplot(src):
    q1 = np.percentile(src, 25)  # Primer cuartil
    q2 = np.percentile(src, 50)  # Mediana
    q3 = np.percentile(src, 75)  # Tercer cuartil
    iqr = q3 - q1  # Rango intercuantil
    lower_bound = q1 - 1.5 * iqr  # Límite inferior
    upper_bound = q3 + 1.5 * iqr  # Límite superior
    bias = 'none'
    left = any(x < lower_bound for x in src)
    right = any(x > upper_bound for x in src)
    if left and right:
        bias = 'both'
    elif left:
        bias = 'left'
    elif right:
        bias = 'right'
    return {
        'q1': q1, 'q2': q2, 'q3': q3, 'iqr': iqr,
        'inf': lower_bound, 'sup': upper_bound,
        'bias': bias, 'left': left, 'right': right
    }

# Función que calcula el rango de confianza al nivel especificado


def confidence_range(src, level=100, box=None):
    if not box:
        box = boxplot(src)
    alpha = 1 - level / 100.0
    if box['left'] and not box['right']:
        return np.quantile(src, [alpha, 1])
    if box['right'] and not box['left']:
        return np.quantile(src, [0, 1 - alpha])
    return np.quantile(src, [alpha / 2, 1 - alpha / 2])

# Función que ajusta los datos y calcula el número de bins para un histograma


def histplot(src, level=100):
    box = confidence_range(src, level=level)
    src = src[(src >= box[0]) & (src <= box[1])]
    bins = 1 + int(np.log2(len(src)))  # Regla de Sturges
    return {
        'serie': src,
        'bins': bins
    }

# Función que realiza un muestreo de la serie de datos


def sample(src, level, deep=1):
    size = len(src) * (level/100.0)
    window = int(len(src) / size)
    size = int(size * deep)
    min = window - 1
    max = len(src) - 1
    index = pd.Series(
        sorted([int(random.uniform(min, max))for _ in range(size)]))
    sample = pd.Series([src[i] for i in index])
    mean = pd.Series([src[i-window+1:i+1].mean() for i in index])
    std = pd.Series([src[i-window+1:i+1].std() for i in index])
    return {
        'index': index,
        'serie': sample,
        'mean': mean,
        'std': std,
        'size': size,
        'window': window
    }


# Función que calcula la Media Móvil Exponencial (EMA)

def ema(series, n):
    alpha = 2 / (n + 1)
    ema = [series[0]]
    for i in range(1, len(series)):
        ema_value = (series[i] - ema[i - 1]) * alpha + ema[i - 1]
        ema.append(ema_value)
    return pd.Series(ema, index=series.index)


# Función que calcula la Media Móvil Simple (SMA)


def sma(src, n=1):
    if (n > 1):
        return src.rolling(window=n).mean()
    return src.copy()


# Función que calcula la Desviación Móvil Simple (SMD)

def smd(src, n=1):
    if (n > 1):
        return sma((src-sma(src, n=n))**2, n - 1) ** 0.5
    return pd.Series([float('nan') for _ in range(len(src))])


# Función que realiza el lag de la serie de datos

def lag(src, n=0):
    if n == 0:
        return src.copy()
    nas = pd.Series([float('nan') for _ in range(abs(n))])
    if n > 0:
        lagged = pd.concat([nas, src[:-n]])
    else:
        lagged = pd.concat([src[-n:], nas])
    return lagged.reset_index(drop=True)

# Función para normalizar (de forma móvil) una serie de datos


def normalizer(src, n, n_lag=1):
    src = lag(src, n_lag)
    mean = sma(src, n)
    std = smd(src, n)

    def norm(src):
        return (src-mean)/std
    return {
        'norm': norm,
        'mean': mean,
        'std': std,
        'src': src
    }


def data_transformer(data, n=2880, mindate='2018-02-12', timescale=60000):
    df = pd.DataFrame()
    ####### Conjunto TOHLCV ######
    df['Time'] = data['Time']
    df['Open'] = data['Open']
    df['High'] = data['High']
    df['Low'] = data['Low']
    df['Close'] = data['Close']
    df['Volume'] = data['Volume']
    ####### LOGARITMO DE VARIABLES ######
    df['Open_Log'] = np.log(data['Open'])
    df['High_Log'] = np.log(data['High'])
    df['Low_Log'] = np.log(data['Low'])
    df['Close_Log'] = np.log(data['Close'])
    df['Volume_Log'] = np.log(1 + data['Volume'])
    ####### NORMALIZACIÓN DE PRECIOS ######
    hl2 = (data['High'] + data['Low']) / 2
    norm = normalizer(hl2, n, n_lag=1)['norm']
    df['Open_Norm'] = norm(data['Open'])
    df['High_Norm'] = norm(data['High'])
    df['Low_Norm'] = norm(data['Low'])
    df['Close_Norm'] = norm(data['Close'])
    df['Close_Rate'] = 100 * (data['Close'] / lag(data['Close'], 1) - 1)
    ####### NORMALIZACIÓN DE VOLUMEN ######
    norm = normalizer(data['Volume'], n, n_lag=0)['norm']
    df['Volume_Norm'] = norm(data['Volume'])
    ####### TRANSFORMACIÓN DE VARIABLES ######
    df['Volume_Qty'] = (data['Volume'] /
                        (data['Volume'] + data['VolumeUSDT'] / data['Close']))
    df['Taker_Prop'] = data['TakerVolume'] / data['Volume']
    df['Volume_Trade'] = data['Volume'] / data['Trades']
    norm = normalizer(df['Volume_Trade'], n, n_lag=0)['norm']
    df['Volume_Trade_Norm'] = norm(df['Volume_Trade'])
    df['Quality'] = ema(1-data['Filled'], 2 * n - 2)
    mintime = pd.Timestamp(mindate).timestamp() * 1000 / timescale
    minindex = max(2 * n - 2, (data['Time'] >= mintime).idxmax())
    df = df.iloc[minindex:]
    df.reset_index(drop=True, inplace=True)
    return df
    ####### Test ######
    dict = {}
    for name in df.columns[1:]:
        value = df[name]
        box = boxplot(value)
        bias = box['bias']
        outliers = round(
            100*(
                sum(value > box['sup']) +
                sum(value < box['inf'])
            )/len(value), 2)
        window = 1000
        sd = value.rolling(window=window).std(
        ).dropna().to_numpy()[::window]
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            kps = kpss(sd, regression='c')[1]
        adf = adfuller(sd)[1]
        dict[name] = {'bias': bias,
                      'outliers': str(outliers) + '%',
                      'test': {
                          'Kpss': str(round(100*kps)) + '%',
                          'Adfuller': str(round(100*adf)) + '%'
                      }
                      }
