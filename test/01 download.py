from src.python.util.basic import load_parameters
from src.python.util.binance import download
from src.python.util.basic import save_arrow


par = load_parameters()

for symbol in par['market symbols']:
    for interval in par['temporality']:
        data = download(
            start=par['start date'],
            end=par['end date'],
            symbol=symbol,
            interval=interval,
            timescale=par['time scale']
        )
        save_arrow(
            data=data,
            file=par['download file'],
            name=symbol + '_' + interval,
            mbytes=par['megabytes limit']
        )
