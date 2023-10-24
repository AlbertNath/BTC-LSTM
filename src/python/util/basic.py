import re
import os
import math
import json
import pandas as pd


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
