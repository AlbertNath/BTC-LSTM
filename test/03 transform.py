"""
TRANSFORMACIÓN DE DATOS
"""

from src.python.util.stats import data_transformer
from src.python.util.basic import load_arrow
from src.python.util.basic import save_arrow

symbol = 'BTCUSDT'
filein = 'data/02 clean'
fileout = 'data/03 transform'
mbytes = 50  # Tamaño recomendado por GitHub

temporality = ['15m', '30m', '1h']
for interval in temporality:
    name = f'BTCUSDT_{interval}'
    data = load_arrow(filein, name)
    data = data_transformer(data)["data"]
    save_arrow(
        data=data[['Time', 'Open', 'High', 'Low', 'Close',
                   'Open_Norm', 'High_Norm', 'Low_Norm', 'Close_Norm',
                   'Volume_Norm', 'Filled_MA', 'Volume_Qty', 'Taker_Prop', 'Volume_Trade']],
        file=fileout,
        name=f'NORM_{symbol}_{interval}',
        mbytes=mbytes
    )
    save_arrow(
        data=data[['Time', 'Open', 'High', 'Low', 'Close',
                   'Open_Log', 'High_Log', 'Low_Log', 'Close_Log',
                   'Volume_Log', 'Volume_Qty', 'Taker_Prop', 'Volume_Trade']],
        file=fileout,
        name=f'LOG_{symbol}_{interval}',
        mbytes=mbytes
    )
