from optimize.constants import *

class Optimizer(object):
    ''' Wrapper for setting up optimization problem and calling solver. '''
    def __init__(self, mean, cov):
        ''' |mean| and |cov| are the return mean and covariance estimates. '''
        if mean.shape[0] != cov.shape[0] or mean.shape[0] != cov.shape[1]:
            raise ValueError(
                'The number of stocks in |mean| must be consistent ' + \
                'with the number of stocks in |cov|, which must be square.')

        self.mean = mean # np.array.shape: (n_stocks,)
        self.cov = cov # np.array.shape: (n_stocks, n_stocks)

    def