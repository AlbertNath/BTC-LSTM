######## python ########

reticulate::use_python("C:\\Python311")
reticulate::source_python("src\\python\\util\\basic.py")

######## Estadísticas ########

# Función para identificar outliers en una serie
outliers <- function(x) {
  box_plot <- boxplot(x, plot = FALSE)
  whisker_lower <- box_plot$stats[1]
  whisker_upper <- box_plot$stats[5]
  list(
    left = any(x < whisker_lower),
    right = any(x > whisker_upper)
  )
}

# Función para calcular el rango de confianza de una serie
conf_range <- function(x, conf.level) { # nolint
  out <- outliers(x)
  alpha <- 1 - conf.level / 100
  if (out$left && !out$right) {
    return(quantile(x, c(alpha, 1), na.rm = TRUE))
  }
  if (out$right && !out$left) {
    return(quantile(x, c(0, 1 - alpha), na.rm = TRUE))
  }
  return(quantile(x, c(alpha / 2, 1 - alpha / 2), na.rm = TRUE))
}

# Función para muestrear estadísticas estadísticas
stats_summary <- function(src, level, window = NULL, index = NULL, deep = 1) {
  index <- itz::isnt.null(index, seq(1, length(src)))
  rang <- range(index)
  sample_size <- round(level * (1 + diff(rang)) / 100)
  window <- itz::isnt.null(window, deep * length(index) / sample_size)
  rang[2] <- rang[2] - window
  sample <- sort(round(runif(sample_size, min = rang[1], max = rang[2])))
  mn <- vector("numeric", length = sample_size)
  vr <- vector("numeric", length = sample_size)
  for (i in 1:sample_size) {
    y <- src[sample[i] + (1:window)]
    mn[i] <- mean(y, na.rm = TRUE)
    vr[i] <- var(y, na.rm = TRUE)
  }
  list(
    sample = sample,
    mean = mn,
    var = vr,
    size = sample_size,
    window = window
  )
}

# Función reaparametrizar linealmente
reparam <- function(src, from = NULL, to = c(0, 1)) {
  if (is.null(from)) {
    from <- range(src, na.rm = TRUE)
  }
  to[1] + (src - from[1]) * (to[2] - to[1]) / (from[2] - from[1])
}


######## Indicadores ########

# Función para calcular rezago en una serie
lag <- function(src, n = 0) {
  if (n == 0) {
    return(src)
  }
  if (n > 0) {
    return(c(rep(NA, n), head(src, -n)))
  }
  c(tail(src, n), rep(NA, -n))
}

# Función para detectar cruces por encima
cross_over <- function(src, ref) {
  src > ref & lag(src, 1) <= lag(ref, 1)
}

# Función para detectar cruces por debajo
cross_under <- function(src, ref) {
  src < ref & lag(src, 1) >= lag(ref, 1)
}

# Función para calcular una relación porcentual
ratio <- function(x, y, xlag = 0, ylag = 0) {
  100 * (lag(x, xlag) / lag(y, ylag) - 1)
}

# Función para calcular estadísticas móviles
stats <- function(src, n, ma = TTR::SMA, ...) {
  tryCatch(
    {
      src_mean <- ma(src, n, ...)
      src_sd <- sqrt(ma((src - src_mean)^2, n - 1, ...))
      return(
        list(
          mean = src_mean,
          sd = src_sd
        )
      )
    },
    error = function(e) {
      return(
        list(
          mean = rep(NA, length(src)),
          sd = rep(NA, length(src))
        )
      )
    }
  )
}

# Función para encontrar el valor más alto en un período
highest <- function(src, n) {
  TTR::runMax(src, n)
}

# Función para encontrar el valor más bajo en un período
lowest <- function(src, n) {
  TTR::runMin(src, n)
}

# Función para realizar normalización móvil de series
normalizer <- function(by, n, ma = TTR::SMA, conf.level = 99, fill = False, ...) { # nolint
  stats <- stats(by, n, ma, ...)
  level <- rep(1, length(by))
  if (fill) {
    mn <- min(which(!is.na(by)))
    stats$mean[1:mn] <- NA
    stats$sd[1:mn] <- NA
    level[1:mn] <- NA
    i <- mn + 1
    sm <- 1
    while (is.na(stats$sd[i]) && i <= length(by)) {
      level[i] <- sm / (2 * (n - 1) - 1)
      index <- max(i - n + 1, mn):i
      stats$mean[i] <- mean(by[index])
      stats$sd[i] <- sd(by[index])
      i <- i + 1
      sm <- sm + 1
    }
  }
  qtl <- qnorm((1 + conf.level / 100) / 2)
  list(
    mean = stats$mean,
    sd = stats$sd,
    norm_level = level,
    norm = function(src) {
      reparam(
        src = (src - stats$mean) / stats$sd,
        from = c(-qtl, qtl),
        to = c(0, 1)
      )
    }
  )
}

# Función para calcular la volatilidad de una serie
volatility <- function(high, low, n = 1, positive = TRUE, ma = TTR::WMA, ...) {
  if (n > 1) {
    if (positive) {
      return(ma(100 * (high / low - 1), n, ...))
    }
    return(ma(100 * (low / high - 1), n, ...))
  }
  if (positive) {
    return(100 * (high / low - 1))
  }
  100 * (low / high - 1)
}

# Función para calcular los límites de stop-loss basados en volatilidad
volatility_stoploss <- function(
    high, low, n, rate = 1, ma = TTR::WMA, src = NULL, ...) {
  src <- if (is.null(src)) ma((high + low) / 2, n, ...) else src
  list(
    src = src,
    inf = src * (1 + rate * volatility(
      high, low,
      n = n, positive = FALSE, ma = ma, ...
    ) / 100),
    sup = src * (1 + rate * volatility(
      high, low,
      n = n, positive = TRUE, ma = ma, ...
    ) / 100)
  )
}

# Función para calcular un indicador LH4
LH4 <- function(high, low, n, level = 0, rate = 1, ma = TTR::SMA, ...) { # nolint
  lh <- (
    highest(low, n) + lowest(high, n) + highest(high, n) + lowest(low, n)
  ) / 4
  lst <- list(lh = lh)
  vol_stop <- volatility_stoploss(
    high = high, low = low, n = n, rate = rate, ma = ma, src = lh, ...
  )
  inf <- vol_stop$inf
  sup <- vol_stop$sup
  if (level > 0) {
    for (i in 1:level) {
      inf_lag <- lag(inf, n)
      sup_lag <- lag(sup, n)
      inf <- pmin(inf, inf_lag, sup_lag)
      sup <- pmax(sup, inf_lag, sup_lag)
      lst[[paste("lh", i * n, sep = "")]] <- lag(lh, i * n)
    }
  }
  lst$inf <- inf
  lst$sup <- sup
  lst
}

# Función para calcular klines Heikin Ashi
heikin_ashi <- function(o, h, l, c) {
  o_ha <- NULL
  h_ha <- NULL
  l_ha <- NULL
  c_ha <- NULL
  n <- length(o)
  for (i in 1:n) {
    if (i == 1 || is.na(o_ha[i - 1]) || is.na(c_ha[i - 1])) {
      o_ha[i] <- (o[i] + c[i]) / 2
    } else {
      o_ha[i] <- (o_ha[i - 1] + c_ha[i - 1]) / 2
    }
    h_ha[i] <- max(h[i], o_ha[i], c[i])
    l_ha[i] <- min(l[i], o_ha[i], c[i])
    c_ha[i] <- (o[i] + h[i] + l[i] + c[i]) / 4
  }
  mat <- cbind(o_ha, h_ha, l_ha, c_ha)
  colnames(mat) <- c("Open", "High", "Low", "Close")
  mat
}
