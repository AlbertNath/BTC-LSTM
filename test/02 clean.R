# Instalación de paquetes necesarios
# install.packages("R6")
# install.packages("TTR")
# install.packages("devtools")
# install.packages("tzdb")
# install.packages("arrow")
# install.packages("corrplot")
# install.packages("reticulate")
# devtools::install_github("artitzco/itz")
# install.packages("jsonlite")

##### limpieza ####
source("src/r/util/basic.R")

par <- jsonlite::fromJSON("src/python/util/parameters.json")

for (temp in par$temporality) {
  name <- paste0(par$"market symbol", "_", temp)
  clean <- clean_data(load_arrow(par$"download file", name))
  save_arrow(clean$data, par$"clean file", name, par$"megabytes limit")
  write.csv(
    clean$block,
    file.path(par$"info file", paste0("BLOCK_", symbol, "_", temp, ".csv"))
  )
}
