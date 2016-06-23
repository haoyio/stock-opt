from constants import *
from estimate.estimator import Estimator

if __name__ == '__main__':
    est = Estimator(TICKER, DATE)
    est.load_data(DATABASE, FILENAME, COMPRESSION, COLUMNS, PARSE_DATES)
    est.crop_date(START, END)
    est.estimate_mean_covariance(COVARIANCE_COLUMN)