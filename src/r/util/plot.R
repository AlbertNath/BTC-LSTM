

# Establecer tema oscuro de gráficos
itz::Plot("col.background", "#151924")
itz::Plot("alp.backlines", 0.1)

# Función para trazar gráficos de velas
candlestick <- function(
    o, h, l, c,
    index = NULL,
    width = 0.25,
    bullish = "#26A69A",
    bearish = "#EF5350",
    doji = "#8A7C75",
    stick = 1,
    newplot = TRUE,
    xlim = NULL,
    ylim = NULL,
    ...) {
  if (is.null(index)) {
    n <- length(o)
    index <- 1:n
  }
  if (newplot) {
    itz::mplot(
      xlim = itz::isnt.null(xlim, c(min(index), max(index))),
      ylim = itz::isnt.null(ylim, range(l, h, na.rm = TRUE)),
      ...
    )
  }
  col <- NULL
  col[c > o] <- bullish
  col[c < o] <- bearish
  col[c == o] <- doji
  for (ind in 1:n) {
    lines(
      c(index[ind], index[ind]),
      c(l[ind], h[ind]),
      lwd = stick,
      col = col[ind]
    )
    rect(
      index[ind] - width,
      o[ind],
      index[ind] + width,
      c[ind],
      col = col[ind],
      border = col[ind]
    )
  }
}

# Función para trazar sombras en un gráfico
shadow <- function(a, b, col) {
  if (length(col) == 1) {
    col[2] <- col[1]
  }
  ranges <- function(x) {
    ranges <- list()
    if (length(x) > 1) {
      current_range <- c(x[1], x[1])
      for (i in 2:length(x)) {
        if (x[i] == x[i - 1] + 1) {
          current_range[2] <- x[i]
        } else {
          ranges <- append(ranges, list(current_range))
          current_range <- c(x[i], x[i])
        }
      }
      ranges <- append(ranges, list(current_range))
    }
    ranges
  }
  range_shadow <- function(a, b, range, color) {
    start <- range[1]
    end <- if (range[2] < length(b)) 1 + range[2] else range[2]
    x <- c(start:end, rev(start:end))
    y <- c(a[start:end], rev(b[start:end]))
    polygon(x, y, col = color, border = NA)
  }
  for (range in ranges(which(a > b))) {
    range_shadow(a, b, range, col[1])
  }
  for (range in ranges(which(a < b))) {
    range_shadow(a, b, range, col[2])
  }
}

# Función para calcular proporciones de un gráfico
proportion <- function(..., size = 6, frame = 1) {
  vec <- unlist(list(...))
  if (length(vec) == 0) {
    vec <- c(frame)
  }
  length <- size * sum(vec) / frame
  list(
    proportion = 100 * vec / sum(vec),
    width = size,
    height = length / 1.618033988749895
  )
}

# Función para trazar líneas verticales en un gráfico
vlines <- function(x, y1, y2, ...) {
  n <- length(x)
  xlist <- NULL
  ylist <- NULL
  for (i in 1:n) {
    xlist[[i]] <- c(x[i], x[i])
    ylist[[i]] <- c(y1[i], y2[i])
  }
  itz::mlines(xlist, ylist, ...)
}

# Función para generar colores aleatorios
samplecolor <- function(n, alpha = 1) {
  rgb(runif(n, 0, 1), runif(n, 0, 1), runif(n, 0, 1), alpha = alpha)
}


# Función para contar rangos continuos
cont_ranges <- function(x) {
  ranges <- list()
  if (length(x) > 1) {
    current_range <- c(x[1], x[1])
    for (i in 2:length(x)) {
      if (x[i] == x[i - 1] + 1) {
        current_range[2] <- x[i]
      } else {
        ranges <- append(ranges, list(current_range))
        current_range <- c(x[i], x[i])
      }
    }
    ranges <- append(ranges, list(current_range))
  }
  ranges
}

# Clase "Graph" para crear gráficos de series
graph_class <- R6::R6Class( # nolint
  classname = "Graph",
  public =
    list(
      vlines = function(serie, ...) {
        private$addgraph(
          range = private$vrange(),
          graph = function(index) {
            abline(v = index[serie[index]], ...)
          }
        )
        self
      },
      hlines = function(values, ...) {
        private$addgraph(
          range = private$vrange(values),
          graph = function(index) {
            abline(h = values, ...)
          }
        )
        self
      },
      lines = function(serie, ...) {
        private$addgraph(
          range = private$srange(serie),
          graph = function(index) {
            itz::mlines(index, serie[index], ...)
          }
        )
        self
      },
      points = function(serie, ...) {
        private$addgraph(
          range = private$srange(serie),
          graph = function(index) {
            points(index, serie[index], ...)
          }
        )
        self
      },
      shadow = function(a_serie, b_serie, col = NULL, alp = 0.3) {
        if (is.null(col)) {
          col <- rep(NULL, 2)
        }
        if (length(col) == 1) {
          col[2] <- col[1]
        }
        private$addgraph(
          range = private$srange(a_serie, b_serie),
          graph = function(index) {
            n <- length(index)
            sa <- a_serie[index]
            sb <- b_serie[index]
            for (rg in cont_ranges(which(sa > sb))) {
              ind <- index[rg[1]:min(rg[2] + 1, n)]
              itz::mshadow(ind, b_serie[ind], ind, a_serie[ind],
                col.shadow = col[1], alp.shadow = alp
              )
            }
            for (rg in cont_ranges(which(sa < sb))) {
              ind <- index[rg[1]:min(rg[2] + 1, n)]
              itz::mshadow(ind, a_serie[ind], ind, b_serie[ind],
                col.shadow = col[2], alp.shadow = alp
              )
            }
          }
        )
        self
      },
      candlestick = function(o, h, l, c,
                             name = NULL,
                             width = 0.5,
                             bullish = "#26A69A",
                             bearish = "#EF5350",
                             doji = "#8A7C75",
                             stick = 1,
                             box = TRUE) {
        width <- width / 2.0
        private$addgraph(
          range = private$srange(o, h, l, c),
          graph = function(index) {
            n <- length(index)
            col <- NULL
            col[c[index] > o[index]] <- bullish
            col[c[index] < o[index]] <- bearish
            col[c[index] == o[index]] <- doji
            for (i in 1:n) {
              lines(c(index[i], index[i]),
                c(l[index[i]], h[index[i]]),
                col = col[i],
                lwd = stick
              )
              if (box) {
                rect(
                  index[i] - width, o[index[i]],
                  index[i] + width, c[index[i]],
                  col = col[i],
                  border = col[i]
                )
              }
            }
          }
        )
        self
      },
      plot = function(at, window = NULL, xlim = NULL, ylim = NULL, ...) {
        if (is.null(window)) {
          indexes <- at
        } else {
          indexes <- (at - window + 1):at
        }
        xlim <- itz::isnt.null(xlim, range(indexes))
        ylim <- itz::isnt.null(ylim, private$range(
          lapply(private$graphs, function(graph) graph$range(indexes))
        ))
        itz::mplot(xlim = xlim, ylim = ylim, ...)
        for (plt in private$graphs) {
          plt$graph(indexes)
        }
      }
    ),
  private =
    list(
      graphs = list(),
      addgraph = function(range, graph) {
        private$graphs[[1 + length(private$graphs)]] <-
          list(range = range, graph = graph)
      },
      range = function(...) {
        rang <- suppressWarnings(range(..., na.rm = TRUE))
        if (rang[1] < rang[2]) {
          return(rang)
        }
        if (rang[1] == rang[2]) {
          return(c(rang[1] - 1, rang[1] + 1))
        }
        NULL
      },
      vrange = function(...) {
        if (length(list(...)) != 0) {
          return(function(index) {
            private$range(...)
          })
        }
        return(function(index) NA)
      },
      srange = function(..., values = NULL) {
        if (length(list(...)) != 0 | !is.null(values)) {
          return(function(index) {
            apply_index <- function(lst) {
              lapply(lst, function(x) {
                if (!is.list(x)) {
                  return(x[index])
                }
                apply_index(x)
              })
            }
            private$range(append(apply_index(list(...)), values))
          })
        }
        return(function(index) NA)
      }
    )
)

# Función para crear una nueva instancia de la clase "Graph"
new.graph <- function() { # nolint
  graph_class$new()
}
