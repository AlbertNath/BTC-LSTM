import pandas as pd
import numpy as np
import random


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


def confidence_range(src, level=100):
    box = boxplot(src)
    alpha = 1 - level / 100.0
    if box['left'] and not box['right']:
        return np.quantile(src, [alpha, 1])
    if box['right'] and not box['left']:
        return np.quantile(src, [0, 1 - alpha])
    return np.quantile(src, [alpha / 2, 1 - alpha / 2])


def histplot(src, level=100):
    box = confidence_range(src, level=level)
    src = src[(src >= box[0]) & (src <= box[1])]
    bins = 1 + int(np.log2(len(src)))  # Regla de Sturges
    return {
        'serie': src,
        'bins': bins
    }


def sample(src, level, deep=1):
    size = len(src) * (level/100.0)
    window = int(len(src) / size)
    size = int(size * deep)
    min = window - 1
    max = len(src) - 1
    index = pd.Series(sorted([int(random.uniform(min, max))for _ in range(size)]))
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
