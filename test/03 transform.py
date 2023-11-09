'''
TRANSFORMACIÓN DE DATOS
'''

from src.python.util.stats import data_transformer
from src.python.util.basic import load_parameters
from src.python.util.basic import load_arrow
from src.python.util.basic import save_arrow
import os

par = load_parameters()

for symbol in par['market symbols']:
    for interval in par['temporality']:
        clean = load_arrow(
            file=par["clean file"],
            name=symbol + '_' + interval
        )
        data, norm = data_transformer(
            clean,
            n=par["normalization window"],
            mindate=par["minimum date"],
            timescale=par["time scale"]
        )
        save_arrow(
            data=data,
            file=par["transform file"],
            name=symbol + '_' + interval,
            mbytes=par["megabytes limit"]
        )
        save_arrow(
            data=norm,
            file=par["info file"],
            name='NORM'+ '_' + symbol + '_' + interval,
            mbytes=par["megabytes limit"]
        )
