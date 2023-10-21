from src.python.util.basic import load_arrow
import matplotlib.pyplot as plt
import numpy as np
import random


def boxplot(data):
    q1 = np.percentile(data, 25)  # Primer cuartil
    q2 = np.percentile(data, 50)  # Mediana
    q3 = np.percentile(data, 75)  # Tercer cuartil
    iqr = q3 - q1  # Rango intercuantil
    lower_bound = q1 - 1.5 * iqr  # Límite inferior
    upper_bound = q3 + 1.5 * iqr  # Límite superior
    bias = "none"
    left = any(x < lower_bound for x in data)
    right = any(x > upper_bound for x in data)
    if left and right:
        bias = "both"
    elif left:
        bias = "left"
    elif right:
        bias = "right"
    return {
        "q1": q1, "q2": q2, "q3": q3, "iqr": iqr,
        "inf": lower_bound, "sup": upper_bound,
        "bias": bias
    }


def sample(src, level, deep=1):
    size = len(src) * (level/100.0)
    window = int(len(src) / size)
    size = int(size * deep)
    min = window - 1
    max = len(src) - 1
    index = sorted([int(random.uniform(min, max))for _ in range(size)])
    sample = [src[i] for i in index]
    mean = [src[i-window+1:i+1].mean() for i in index]
    std = [src[i-window+1:i+1].std() for i in index]
    return {
        'index': index,
        'sample': sample,
        'mean': mean,
        'std': std,
        'size': size,
        'window': window
    }


interval = '30m'
file = 'data/02 clean'
name = f'BTCUSDT_{interval}'
data = load_arrow(file, name)
data

serie = data['Close']

serie.hist(bins=5, edgecolor='k')
plt.xlabel('Valor')
plt.ylabel('Frecuencia')
plt.title('Histograma')
plt.show()
