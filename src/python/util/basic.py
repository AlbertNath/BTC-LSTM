
from src.python.util.stats import confidence_range
from scipy.stats import norm
import pandas as pd
import numpy as np
import math
import json
import re
import os

# Función para guardar una base de datos en sub-bases de tamaño máximo


def save_arrow(data, file, name, mbytes=100):
    # Se calcula el tamaño máximo de cada subase
    join_file = os.path.join(file, f'{name}.arrow')
    data.to_feather(join_file)
    mb = os.path.getsize(join_file) / (1024.0 ** 2)
    n = max(1, math.ceil(mb / mbytes))
    size = len(data) // n
    os.remove(join_file)

    # Se eliminan las coincidencias de archivos f'{jfile}_{i}.arrow'
    patt = re.compile(f'{name}_\d+\.arrow')
    for filename in os.listdir(file):
        if patt.match(filename):
            os.remove(os.path.join(file, filename))

    # Se es guardan los datos en sub-bases de tamaño máximo size
    for i in range(n):
        start = i * size
        end = (i + 1) * size if i < n - 1 else len(data)
        sub_data = data.iloc[start:end]
        sub_data.to_feather(os.path.join(file, f'{name}_{i}.arrow'))

# Función para lee sub-bases de datos


def load_arrow(file, name):
    patt = re.compile(f'{name}_\d+\.arrow')
    data_list = []
    for filename in os.listdir(file):
        if patt.match(filename):
            df = pd.read_feather(os.path.join(file, filename))
            data_list.append(df)
    return pd.concat(data_list)


def save_json(file, dict):
    with open(file, 'w') as file:
        json.dump(dict, file, indent=4)


def load_json(file):
    with open(file, 'r') as file:
        return json.load(file)


def load_parameters():
    return load_json('src/python/util/parameters.json')


def datasets(symbol, interval, variables=[], subsets=[], conf_level=99, isolated=False):
    par = load_parameters()
    if symbol not in par['market symbols']:
        raise Exception(
            f'Error: Market symbol "{symbol}" not found. \n\tPlease check the "src/python/util/parameters.json" file.')

    if interval not in par['temporality']:
        raise Exception(
            f'Error: Temporality "{interval}" not found. \n\tPlease check the "src/python/util/parameters.json" file.')
    data = load_arrow(par['transform file'], symbol + '_' + interval)
    data = data[[
        'Time',
        'Open',
        'High',
        'Low',
        'Close',
        'Volume'
    ] + variables]
    sizes = np.array([len(data)] if not subsets else subsets)
    if sum(sizes) > len(data):
        raise Exception(
            'The total size of subsets is greater than the length of the data.')
    if any(sizes <= 0):
        raise Exception('Some subset size is zero or negative.')
    time = pd.to_datetime(data['Time'] * par['time scale'], unit='ms')
    index = np.append(0, np.cumsum(sizes))
    subdata = [data.iloc[index[i - 1]:index[i]]
               for i in range(1, len(index))]

    excedent = len(data) - sum(sizes)
    sizes = np.append(sizes, excedent)
    index = np.append(0, np.cumsum(sizes))
    prop = np.round(100 * sizes / len(data), 2)

    if excedent > 0:
        time = [time[index[i - 1]] for i in range(1, len(index))]
    else:
        time = [time[index[i - 1]] for i in range(1, len(index) - 1)] + ['-']

    ######## Estandarización ########
    def stand_ranges(df, name):
        if name == 'Noise':
            return np.array([0, 1])
        if name.endswith("_Norm") and conf_level < 100:
            qnorm = norm.ppf((1 - conf_level / 100) / 2)
            return np.array([qnorm, -qnorm])
        return confidence_range(df[name], conf_level)

    stand_subdata = subdata if isolated else [subdata[0]] * len(subdata)
    ranges = pd.DataFrame(
        [[stand_ranges(data, name) for name in variables]
         for data in stand_subdata], columns=variables)

    for index, df in enumerate(subdata):
        for name in variables:
            rang = ranges.loc[index, name]
            df.loc[:, name] = (df[name] - rang[0]) / (rang[1] - rang[0])

    ######## Resumen ########
    summary = pd.DataFrame()
    summary["size"] = sizes
    summary["prop"] = [str(x) + "%" for x in prop]
    summary["time"] = time
    summary.index = ['ABCDEFGHIJKLMNOPQRSTUVWXYZ'[i]
                     for i in range(len(summary) - 1)] + ['not assigned']
    print(summary.to_string())

    ######## Desnormalización ########
    normstats = load_arrow(file=par['info file'],
                           name='NORM' + '_' + symbol + '_' + interval)
    norm_window = par["normalization window"]

    def inverse(src, time):
        for index in range(len(subdata)):
            if time in subdata[index]['Time'].values:
                rang = ranges.loc[index, 'Close_Norm']
                break
            else:
                raise Exception('"time" not found.')
        # Índices históricos
        start = norm_window - 1
        b_index = np.where(normstats["time"] == time)[0][0]
        a_index = b_index - start

        # Serie histórica
        close = np.concatenate(
            [normstats["src"].iloc[a_index: b_index], rang[0] + (rang[1] - rang[0]) * src])
        sqdif = np.concatenate(
            [(normstats["src"].iloc[a_index: b_index] -
              normstats["mean"].iloc[a_index: b_index]) ** 2.0,
             np.array([np.nan] * len(src))
             ])
        # Des-estandarización
        close[start] = (normstats["mean"].iloc[b_index - 1] +
                        normstats["std"].iloc[b_index - 1] * close[start])

        for i in range(start + 1, len(close)):
            mean = close[i - norm_window: i].mean()
            sqdif[i - 1] = (close[i - 1] - mean) ** 2.0
            sd = (sqdif[i - norm_window + 1: i].mean()) ** 0.5
            close[i] = mean + sd * close[i]
            src = src.copy()
            src[:] = close[start:]
        return src
    return tuple(subdata + [inverse])
