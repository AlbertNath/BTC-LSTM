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

param <- jsonlite::fromJSON("test/param.json")

symbol <- "BTCUSDT"
filein <- "data/01 download"
fileout <- "data/02 clean"
block <- "data/info"
mbytes <- 50 # Tamaño recomendado por GitHub

for (temp in param$temporality) {
  name <- paste0(symbol, "_", temp)
  clean <- clean_data(load_arrow(filein, name))
  save_arrow(clean$data, fileout, name, mbytes)
  write.csv(
    clean$block,
    file.path(block, paste0("BLOCK_", symbol, "_", temp, ".csv"))
  )
}
