import numpy as np
import pandas as pd
import quandl; quandl.ApiConfig.api_key = 'xTgtE7sE8hHsnGSQij-E'
import time

from sklearn.covariance import LedoitWolf, OAS, ShrunkCovariance, \
    empirical_covariance, log_likelihood
from sklearn.grid_search import GridSearchCV

DATABASE = 'WIKI'
FILENAME = '../data/wiki.zip'
COMPRESSION = 'zip'
PARSE_DATES = [1]

COLUMNS = [
    'ticker',
    'date',
    'open',
    'high',
    'low',
    'close',
    'volume',
    'ex_dividend',
    'split_ratio',
    'adj_open',
    'adj_high',
    'adj_low',
    'adj_close',
    'adj_volume'
]
