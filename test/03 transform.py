'''
TRANSFORMACIÓN DE DATOS
'''

import os
import json
from src.python.util.stats import data_transformer
from src.python.util.basic import load_arrow
from src.python.util.basic import save_arrow

with open('test/param.json', 'r') as json_file:
    param = json.load(json_file)

symbol = 'BTCUSDT'
filein = 'data/02 clean'
fileout = 'data/03 transform'
mbytes = 50  # Tamaño recomendado por GitHub

for interval in param['temporality']:
    name = f'BTCUSDT_{interval}'
    clean = load_arrow(filein, name)
    transf = data_transformer(clean)
    save_arrow(
        data=transf['data'],
        file=fileout,
        name=f'{symbol}_{interval}',
        mbytes=mbytes
    )
    archivo_json = os.path.join(
        'data/info', "RANGE_"+symbol+'_'+interval+'.json')
    with open(archivo_json, 'w') as file:
        json.dump(transf['range'], file, indent=4)
