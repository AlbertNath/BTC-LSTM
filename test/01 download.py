from src.python.util.binance import download
from src.python.util.basic import save_arrow
from src.python.util.basic import load_json

par = load_json('src/python/util/parameters.json')

for interval in par['temporality']:
    data = download(
        start=par['start date'],
        end=par['end date'],
        symbol=par['market symbol'],
        interval=interval,
        timescale=par['time scale']
    )
    save_arrow(
        data=data,
        file=par['download file'],
        name=par['market symbol'] + f'_{interval}',
        mbytes=par['megabytes limit']
    )
