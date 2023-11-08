
from src.python.util.stats import confidence_range

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
    n = max(1, math.ceil(mb/mbytes))
    size = len(data)//n
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
    if subsets:
        sizes = np.array(subsets)  # np.array([subsets[x] for x in subsets])
        if sum(sizes) > len(data):
            raise Exception(
                'The total size of subsets is greater than the length of the data.')
        if any(sizes <= 0):
            raise Exception('Some subset size is zero or negative.')
        time = pd.to_datetime(data['Time']*par['time scale'], unit='ms')
        index = np.append(0, np.cumsum(sizes))
        subdata = [data.iloc[index[i-1]:index[i]]
                   for i in range(1, len(index))]

        excedent = len(data) - sum(sizes)
        sizes = np.append(sizes, excedent)
        index = np.append(0, np.cumsum(sizes))
        prop = np.round(100*sizes/len(data), 2)

        if excedent > 0:
            time = [time[index[i-1]] for i in range(1, len(index))]
        else:
            time = [time[index[i-1]] for i in range(1, len(index)-1)] + ['-']

        if isolated:
            for data in subdata:
                for name in variables:
                    rang = confidence_range(data[name], conf_level)
                    data[name] = (data[name]-rang[0])/(rang[1]-rang[0])
        else:
            ranges = [confidence_range(subdata[0][name], conf_level)
                      for name in variables]
            for data in subdata:
                for name, rang in zip(variables, ranges):
                    data[name] = (data[name]-rang[0])/(rang[1]-rang[0])

        ###########
        status = pd.DataFrame()
        status["size"] = sizes
        status["prop"] = [str(x)+"%" for x in prop]
        status["time"] = time
        status.index = ['ABCDEFGHIJKLMNOPQRSTUVWXYZ'[i]
                        for i in range(len(status)-1)] + ['not assigned']
        print(status.to_string())
        return tuple(subdata)

    return data
