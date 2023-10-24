'''
TRANSFORMACIÓN DE DATOS
'''
from src.python.util.stats import data_transformer
from src.python.util.basic import load_arrow
from src.python.util.basic import save_arrow
from src.python.util.basic import load_json
from src.python.util.basic import save_json
import os

par = load_json('src/python/util/parameters.json')

par["scale time"]
for interval in par['temporality']:
    name = par['market symbol'] + f'_{interval}'
    clean = load_arrow(par["clean file"], name)
    transf = data_transformer(
        clean,
        n=par["normalization window"],
        mindate=par["minimum date"],
        level=par["confidence range level"],
        test=par["test data ratio"],
        timescale=par["time scale"]
    )
    save_arrow(
        data=transf['data'],
        file=par["transform file"],
        name=par['market symbol'] + f'_{interval}',
        mbytes=par["megabytes limit"]
    )
    json_file = os.path.join(
        par["info file"], "RANGE_" + par['market symbol'] + '_' + interval + '.json')
    save_json(json_file,  transf['range'])
