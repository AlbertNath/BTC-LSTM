# Instalación de paquetes necesarios
# install.packages("corrplot")
# install.packages("arrow")
# devtools::install_github("artitzco/itz")

##### Análisis inicial #####
source("src/r/util/basic.R")
source("src/r/util/plot.R")

data <- load_arrow("data\\02 clean", "BTCUSDT_1h")


# Función para graficar estadísticas de muestreos aleatorios

plot_sample <- function(
    src, level, window = NULL, index = NULL, deep = 1, mean = TRUE, conf.level = 100, ...) { # nolint
  st <- stats_summary( # nolint
    src = src,
    level = level,
    window = window,
    index = index,
    deep = deep
  )
  col <- samplecolor(st$size) # nolint
  src <- if (mean) st$mean else src <- st$var
  itz::mplot(
    xlim = range(st$sample),
    ylim = conf_range(src, conf.level), # nolint
    ...
  )
  points(st$sample, src, col = col, pch = 20, cex = 0.2)
  print(paste("Sample size:", st$size, " Window:", round(st$window)))
}

# Análisis de correlograma
.data <- data
.data$Filled <- NULL
.data$Time <- data$Time / 100000
corrplot::corrplot(cor(.data), method = "color")

# Generación de gráficos

plot_sample(data$Close, level = 0.25)

plot_sample(log(data$Close), level = 0.25)

itz::mhist(log(data$Close))

plot_sample(data$Volume, level = 0.25)

plot_sample(log(1 + data$Volume), level = 0.25)

itz::mhist(log(1 + data$Volume))

##### Generación de series representativas #####


##### Segundo análisis #####



##### Análisis de varianzas #####
