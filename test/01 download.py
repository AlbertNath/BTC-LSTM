"""
DESCARGA DE DATOS

Este código tiene como objetivo descargar datos de un par de criptomonedas
listado en el exchange Binance. Los datos se obtienen en distintas temporalidades, 
que incluyen "1m" (1 minuto), "15m" (15 minutos), "30m" (30 minutos), "1h" (1 hora) y "1d" (1 día).

El rango de tiempo para la descarga está configurado desde '2017-01-01 00:00:00' 
hasta '2024-01-01 00:00:00'. El par de criptomonedas elegido es 'BTCUSDT'.

Los datos descargados se guardan en el directorio 'data/01 download'.
GitHub sugiere que el tamaño máximo de cada archivo sea de 50 megabytes (mbytes)
"""
import json
from src.python.util.binance import download
from src.python.util.basic import save_arrow

with open('test/param.json', 'r') as json_file:
    param = json.load(json_file)


start = '2017-01-01 00:00:00'
end = '2024-01-01 00:00:00'
symbol = 'BTCUSDT'
file = 'data/01 download'
mbytes = 50  # Tamaño recomendado por GitHub

for interval in param['temporality']:
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
