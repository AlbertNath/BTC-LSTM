
from src.python.util.binance import download
from src.python.util.basic import save_arrow

############ Descarga de datos de Binance ############

for interval in ['1m', '15m','30m', '1h']:
    data = download(
        start='2017-01-01 00:00:00',
        end='2024-01-01 00:00:00',
        symbol='BTCUSDT',
        interval=interval
    )
    save_arrow(
        data=data,
        file='data\\01 download',
        name=f'BTCUSDT_{interval}',
        mbytes=100
    )
