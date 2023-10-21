# Librerías necesarias
# pip install python-binance #https://python-binance.readthedocs.io/en/latest/
# pip install pyarrow

# Función para descargar datos de Binance
from src.python.util.binance import download
# Función para guardar sub-bases de datos
from src.python.util.basic import save_arrow
# Función para leer sub-bases de datos
from src.python.util.basic import load_arrow

############ Ejemplo de descarga de datos de Binance ############

data = download(
    start='2023-08-01 00:00:00',  # Tiempo de inicio
    end='2023-09-20 00:00:00',  # Tiempo final
    symbol='BTCUSDT',  # Tiempo final
    interval='5m'  # Temporalidad (_s, _m, _h, _d)
)

############ Ejemplo de guardar base en sub-bases con un tamaño máximo ############

save_arrow(
    data=data,  # Base de datos
    file='test/.trash',  # Ubicación del archivo de salida
    name='dataBTC',  # Nombre del archivo de salida sin extensión
    # Tamaño máximo MB (por defecto 100, el tamaño máximo en GihHub)
    mbytes=0.05
)

############ Ejemplo de leer sub-bases de datos guardadas con save_arrow ############

data1 = load_arrow(
    file='test/.trash',  # Ubicación del archivo
    name='dataBTC'  # Nombre del archivo sin extensión
)

###### Prueba de que parece que si funciona XD ############

# Guardamos otro grupo con diferente tamaño máximo:
save_arrow(data, 'test/.trash', 'dataBTC', 0.1)
data2 = load_arrow('test/.trash', 'dataBTC')

# data, data1 y data2 deben de ser iguales:
data.equals(data1)
data.equals(data2)

############ Limpieza de datos ###########
# Los datos de precios del par BTCUSDT fueron descargados en temporalidades
# de 1m, 30m y 1h y guardados en 'data/01 download', porteriormente fueron tratados
# por métodos de interpolación para completar la información faltante, los resultados
# fueron guardados en 'data/01 clean. Los detalles de las bases tratadas pueden encontrarse
# en 'data/info/block...csv'


############ BASES DE DATOS LIMPIAS Y LISTAS PARA USAR  \o\ ###########

# Temporalidad de 1m: 3,247,838 de renglones
load_arrow('data/02 clean', 'BTCUSDT_1m')

# Temporalidad de 15m: 216,523 de renglones
load_arrow('data/02 clean', 'BTCUSDT_15m')

# Temporalidad de 30m: 108,262 de renglones
load_arrow('data/02 clean', 'BTCUSDT_30m')

# Temporalidad de 1h: 54,131 de renglones
load_arrow('data/02 clean', 'BTCUSDT_1h')

# Temporalidad de 1d: 2,256de renglones
load_arrow('data/02 clean', 'BTCUSDT_1d')
