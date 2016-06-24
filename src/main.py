from estimate.estimator import Estimator
from optimize.optimizer import Optimizer

if __name__ == '__main__':
    est = Estimator(
        ticker_column='ticker',
        date_column='date')

    est.load_data(
        database='WIKI',
        filename='../data/wiki.zip',
        compression='zip',
        columns=[
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
            'adj_volume'],
        parse_dates=[1],
        download=False)

    est.crop_date(start='2012-06-01', end='2016-06-01')
    est.estimate_mean_covariance(column='close')

    opt = Optimizer(est.mean_log, est.cov_ml); opt.solve()
    opt.cov = est.cov_sh; opt.solve()
    opt.cov = est.cov_lw; opt.solve()
    opt.cov = est.cov_oa; opt.solve()
    opt.show()
