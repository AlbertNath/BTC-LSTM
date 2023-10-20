import pandas as pd
from src.python.util.binance import download
from src.python.util.basic import save_arrow

############ Descarga de datos de Binance ############

start = '2017-01-01 00:00:00'
end = '2024-01-01 00:00:00'
symbol = 'BTCUSDT'
temporality = ['1m', '15m', '30m', '1h', '1d']
file = 'data\\01 download'
mbytes = 50  # Tamaño recomendado por GitHub

for interval in temporality:
    data = download(
        start=start,
        end=end,
        symbol=symbol,
        interval=interval
    )
    save_arrow(
        data=data,
        file=file,
        name=f'{symbol}_{interval}',
        mbytes=mbytes
    )
