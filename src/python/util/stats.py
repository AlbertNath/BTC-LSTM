import pandas as pd
import numpy as np
import random

# Función que calcula los estadísticos para un diagrama de caja


def boxplot(src):
    q1 = np.percentile(src, 25)  # Primer cuartil
    q2 = np.percentile(src, 50)  # Mediana
    q3 = np.percentile(src, 75)  # Tercer cuartil
    iqr = q3 - q1  # Rango intercuantil
    lower_bound = q1 - 1.5 * iqr  # Límite inferior
    upper_bound = q3 + 1.5 * iqr  # Límite superior
    bias = "none"
    left = any(x < lower_bound for x in src)
    right = any(x > upper_bound for x in src)
    if left and right:
        bias = "both"
    elif left:
        bias = "left"
    elif right:
        bias = "right"
    return {
        "q1": q1, "q2": q2, "q3": q3, "iqr": iqr,
        "inf": lower_bound, "sup": upper_bound,
        "bias": bias, "left": left, 'right': right
    }

# Función que calcula el rango de confianza al nivel especificado


def confidence_range(src, level=100):
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

# Función que calcula la Media Móvil Simple (SMA)


def sma(src, n=1):
    if (n > 1):
        return src.rolling(window=n).mean()
    return src


# Función que calcula la Desviación Móvil Simple (SMD)

def smd(src, n=1):
    if (n > 1):
        return sma((src-sma(src, n=n))**2, n - 1) ** 0.5
    return pd.Series([float("nan") for _ in range(len(src))])


# Función que realiza el lag de la serie de datos

def lag(src, n=0):
    if n == 0:
        return src
    nas = pd.Series([float("nan") for _ in range(abs(n))])
    if n > 0:
        lagged = pd.concat([nas, src[:-n]])
    else:
        lagged = pd.concat([src[-n:], nas])
    return lagged.reset_index(drop=True)

# Función para normalizar (de forma móvil) una serie de datos


def normalizer(src, n, lg=1):
    src = lag(src, lg)
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
