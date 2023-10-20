# Instalación de paquetes necesarios
# install.packages("R6")
# install.packages("TTR")
# install.packages("devtools")
# install.packages("tzdb")
# install.packages("arrow")
# install.packages("reticulate")
# devtools::install_github("artitzco/itz")

##### limpieza #####

source("src/r/util/basic.R")

# Función de interpolación lineal
lineal <- function(start, end, a, b = NULL, from = NULL, to = NULL) {
  b <- itz::isnt.null(b, a)
  return(
    reparam( # nolint
      start:end,
      from = itz::isnt.null(from, c(start - 1, end + 1)),
      to = itz::isnt.null(to, c(a[start - 1], b[end + 1]))
    )
  )
}

# Función para aproximar de forma lineal los datos faltantes
clean_data <- function(data, left.lag = 1, right.lag = 2, scalet = 60000) { # nolint
  interval <- min(diff(data$Time))
  index <- (interval + data$Time - min(data$Time)) / interval
  time <- min(data$Time) + seq(0, max(index) - 1) * interval
  open <- NULL
  high <- NULL
  low <- NULL
  close <- NULL
  volume <- NULL
  volume_usdt <- NULL
  taker_volume <- NULL
  taker_volume_usdt <- NULL
  trades <- NULL
  open[index] <- data$Open
  high[index] <- data$High
  low[index] <- data$Low
  close[index] <- data$Close
  volume[index] <- data$Volume
  volume_usdt[index] <- data$VolumeUSDT
  taker_volume[index] <- data$TakerVolume
  taker_volume_usdt[index] <- data$TakerVolumeUSDT
  trades[index] <- data$Trades
  filled <- rep(0, max(index))
  jumps <- which(diff(index) > 1) + 1
  hl2 <- (close + high) / 2
  for (i in jumps) {
    start <- index[i - 1] - left.lag + 1
    end <- index[i] + right.lag - 1
    ival <- start:end
    lag_ival <- ival - end + start - 1
    filled[ival] <- 1
    close[ival] <- lineal(start, end, close, open, from = c(start - 1, end))
    open[ival] <- close[ival - 1]
    med <- lineal(start, end, hl2)
    vol <- mean((high[lag_ival] - low[lag_ival]) / 2)
    high[ival] <- pmax(med + vol, open[ival], close[ival])
    low[ival] <- pmin(med - vol, open[ival], close[ival])
    volume[ival] <- mean(volume[lag_ival])
    volume_usdt[ival] <- mean(volume_usdt[lag_ival])
    taker_volume[ival] <- mean(taker_volume[lag_ival])
    taker_volume_usdt[ival] <- mean(taker_volume_usdt[lag_ival])
    trades[ival] <- mean(trades[lag_ival])
  }

  start <- c(1, which(diff(filled) == -1) + 1)
  end <- c(which(diff(filled) == 1), length(filled))
  return(
    list(
      block = data.frame(
        Date = as.POSIXct(time[start] * scalet / 1000, tz = "UTC"),
        Start = start - 1,
        End = end - 1,
        Size = end - start + 1,
        Filled = c(diff(cumsum(filled)[start]), 0)
      ),
      data = data.frame(
        Time = time,
        Open = open,
        High = high,
        Low = low,
        Close = close,
        Volume = volume,
        VolumeUSDT = volume_usdt,
        TakerVolume = taker_volume,
        TakerVolumeUSDT = taker_volume_usdt,
        Trades = trades,
        Filled = filled
      )
    )
  )
}



# Limpieza de datos para intervalo de 1 minuto
clean <- clean_data(load_arrow("data\\01 download", "BTCUSDT_1m"))
save_arrow(clean$data, "data\\02 clean\\", "BTCUSDT_1m")
write.csv(clean$block, "data/info/block_BTCUSDT_1m.csv")


# Limpieza de datos para intervalo de 30 minutos
clean <- clean_data(load_arrow("data\\01 download", "BTCUSDT_30m"))
save_arrow(clean$data, "data\\02 clean\\", "BTCUSDT_30m")
write.csv(clean$block, "data/info/block_BTCUSDT_30m.csv")

# Limpieza de datos para intervalo de 1 hora
clean <- clean_data(load_arrow("data\\01 download", "BTCUSDT_1h"))
save_arrow(clean$data, "data\\02 clean\\", "BTCUSDT_1h")
write.csv(clean$block, "data/info/block_BTCUSDT_1h.csv")

##### Gráficas #####

source("src/r/util/plot.R")

attach(load_arrow("data\\02 clean", "BTCUSDT_1h"))

graph <- new.graph()$
  candlestick(Open, High, Low, Close)

step <- 2
start <- 7508
counter <- itz::newCount(start, step)
window <- 100

graph$plot(counter$getPlus(), 100)
