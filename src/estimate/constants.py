import numpy as np
import pandas as pd
import quandl; quandl.ApiConfig.api_key = 'xTgtE7sE8hHsnGSQij-E'
import time

from datetime import datetime
from sklearn.covariance import LedoitWolf, OAS, ShrunkCovariance, \
    empirical_covariance, log_likelihood
from sklearn.grid_search import GridSearchCV

DATELEN = 10