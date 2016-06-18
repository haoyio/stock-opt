from constants import *
from estimate.estimator import Estimator

if __name__ == '__main__':
    est = Estimator()
    est.load_data(DATABASE, FILENAME, COMPRESSION, COLUMNS, PARSE_DATES)
    print est.df.dtypes