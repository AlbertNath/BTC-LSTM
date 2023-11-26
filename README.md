#### Computer Science Seminar A: Neurons and neural networks: models and applications to data science. 

# Time series forecast using LSTM architecture 

---
A neural network aiming to forecast BTC/USDT stock prices using the LSTM architecture. Implemented 
using [TensorFlow](https://www.tensorflow.org/) and the [Keras](https://keras.io/) API. Hyperparameter tuning
was implemented using [scikit-learn](https://scikit-learn.org/stable/index.html) and KerasRegressor from 
SciKeras.

### Data

Source data was retrieved from [Binance](https://www.binance.com/en) API using different intervals of time. You 
can look at raw and processed data in the `data/` directory. Also, at `data/info` you can find details for
every dataset about the data and added (filled) values due to missing intervals of time from the API. 

Details about data analysis and processing can be found at `src/python/jnotes` (currently in Spanish). Some 
auxiliary functions used in the notebooks are at `src/python/util`.

### Model 

Model hyperparameter tuning and training with a simple prediction test can be reviewed at
`src/python/jnotes/model`. 

### Developed by
- [AlbertNath](https://github.com/AlbertNath)
- [BritnyBrito](https://github.com/BritnyBrito)
- [Medina Ruiz A. I.](https://github.com/artitzco)
- [TaniaRmz](https://github.com/TaniaRmz)
