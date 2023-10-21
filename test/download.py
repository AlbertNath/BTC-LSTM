"""
DESCARGA DE DATOS DE CRIPTOMONEDAS DESDE BINANCE

Este código tiene como objetivo descargar datos de un par de criptomonedas
listado en el exchange Binance. Los datos se obtienen en distintas temporalidades, 
que incluyen "1m" (1 minuto), "15m" (15 minutos), "30m" (30 minutos), "1h" (1 hora) y "1d" (1 día).

El rango de tiempo para la descarga está configurado desde '2017-01-01 00:00:00' 
hasta '2024-01-01 00:00:00'. El par de criptomonedas elegido es 'BTCUSDT'.

Los datos descargados se guardan en el directorio 'data/01 download'.
GitHub sugiere que el tamaño máximo de cada archivo sea de 50 megabytes (mbytes)
"""

from src.python.util.binance import download
from src.python.util.basic import save_arrow

start = '2017-01-01 00:00:00'
end = '2024-01-01 00:00:00'
symbol = 'BTCUSDT'
temporality = ['1m', '15m', '30m', '1h', '1d']
file = 'data/01 download'
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
