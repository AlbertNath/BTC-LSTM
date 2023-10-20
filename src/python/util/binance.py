
from src.python.util.basic import save_arrow
from dateutil.relativedelta import relativedelta
from binance.client import Client
import time as sys_time
import pandas as pd


# Función para calcular un valor de tiempo basado en el intervalo y el paso


def _step_time(interval, step):
    if interval.endswith('m'):
        interval = pd.to_timedelta(int(interval[:-1]), unit='m')
    elif interval.endswith('s'):
        interval = pd.to_timedelta(int(interval[:-1]), unit='s')
    elif interval.endswith('h'):
        interval = pd.to_timedelta(int(interval[:-1]), unit='h')
    elif interval.endswith('d'):
        interval = pd.to_timedelta(int(interval[:-1]), unit='d')
    elif interval.endswith('M'):
        interval = relativedelta(months=int(interval[:-1]))
    return interval * step


# Creación de una instancia del cliente de Binance
client = Client()

# Función para obtener klines históricos de un par de activos y un intervalo de tiempo


def _get_klines(start_time, end_time, symbol='BTCUSDT', interval='1m', limit=1000, scalet=60000):
    klines_list = client.get_klines(
        symbol=symbol,
        interval=interval,
        startTime=int(start_time.timestamp()*1000),
        endTime=int(end_time.timestamp()*1000),
        limit=limit
    )
    data = []
    for klines in klines_list:
        data.append(
            [
                klines[0]/scalet,
                float(klines[1]),
                float(klines[2]),
                float(klines[3]),
                float(klines[4]),
                float(klines[5]),
                float(klines[7]),
                float(klines[9]),
                float(klines[10]),
                int(klines[8])
            ]
        )
    if data:
        return {'data': data,
                'start': pd.Timestamp(scalet*data[0][0], unit='ms'),
                'end': pd.Timestamp(scalet*data[len(data)-1][0], unit='ms')}
    return {'data': data,
            'start': start_time,
            'end': end_time}

# Función para descargar datos en un rango de fechas y con un intervalo de tiempo dado


def download(start, end, symbol='BTCUSDT', interval='1m', limit=1000, unit='s'):
    start = pd.Timestamp(start, unit=unit)
    end = min(pd.Timestamp(end, unit=unit), pd.Timestamp.now())
    start_time = start
    end_time = min(end, start_time +
                   _step_time(interval=interval, step=limit-1))
    data = []
    seconds = sys_time.time()
    percentage = 0
    count = 0
    while start_time <= end_time:
        count += 1
        klines_list = _get_klines(start_time=start_time,
                                  end_time=end_time,
                                  symbol=symbol,
                                  interval=interval,
                                  limit=limit)
        data += klines_list['data']
        diftime = sys_time.time()-seconds
        percen = int(100*((end_time - start)/(end-start)))
        start_time = klines_list['end'] + _step_time(interval=interval, step=1)
        end_time = min(end, start_time +
                       _step_time(interval=interval, step=limit-1))
        if percen > percentage or \
                (start_time > end_time and percentage != 100):
            percentage = percen
            print(
                f'Avance: {percentage}%' +
                f'  consultas: {count}' +
                f'  segundos: {round( diftime,2)}' +
                f'  tasa: {round(count/diftime,2)}')
    return pd.DataFrame(data,
                        columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume',
                                 'VolumeUSDT', 'TakerVolume', 'TakerVolumeUSDT', 'Trades'])
