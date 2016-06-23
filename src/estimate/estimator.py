from estimate.constants import *

class Estimator(object):
    ''' Wrapper for loading stock price data and estimating covariance. '''
    def __init__(self, ticker_column, date_column):
        self.ticker = ticker_column # column name for tickers; e.g., 'ticker'
        self.date = date_column # column name for timestamps; e.g., 'date'

        self.df = None # stock price dataframe
        self.mean_log = None # mean return estimate using log(p_t/p_t-1)
        self.mean_std = None # mean return estimate using (p_t-p_t-1)/p_t-1

        self.cov_ml = None # maximum likelihood covariance estimate
        self.cov_sh = None # covariance estimate with shrinkage
        self.cov_lw = None # Ledoit-Wolf shrinkage estimate
        self.cov_oa = None # oracle approximating shrinkage estimate

    def load_data(
            self,
            database,
            filename,
            compression,
            columns,
            parse_dates,
            download=False):
        ''' Returns |database| as a pandas DataFrame. '''
        if download:
            print 'INFO: Downloading ' + database + ' database into ' + filename
            start_time = time.clock()

            quandl.bulkdownload(database, filename=filename)

            print 'INFO: ' + database + ' download completed in ' + \
                str(int((time.clock() - start_time) / 60)) + ' min'

        print 'INFO: Loading ' + filename
        start_time = time.clock()

        self.df = pd.read_csv(
            filename,
            compression=compression,
            parse_dates=parse_dates)
        self.df.columns = columns

        print 'INFO: ' + filename + ' loaded in ' + \
            str(int(time.clock() - start_time)) + ' sec'

    def crop_date(self, start, end):
        '''
        Crops |self.df| to |start| and |end| (exclusive) date strings with format 'YYYY-MM-DD' and keep only stock tickers that are found in both
        the |start| and |end| dates.
        '''
        print 'INFO: Cropping date range to ' + start + ' and ' + end

        s = [int(i) for i in start.split('-')]
        e = [int(i) for i in end.split('-')]

        # crop dates
        self.df = self.df[ \
            (self.df[self.date] >= \
                datetime(year=s[0], month=s[1], day=s[2])) & \
            (self.df[self.date] < \
                datetime(year=e[0], month=e[1], day=e[2]))]
        self.df = self.df.reset_index(drop=True)

        # find list of stocks that exist between |start| and |end|
        stix = set(self.df[self.df[self.date] == \
                   self.df[self.date].min()][self.ticker].values)
        etix = set(self.df[self.df[self.date] == \
                   self.df[self.date].max()][self.ticker].values)
        tickers = stix.intersection(etix)

        print 'INFO: ' + str(len(tickers)) + \
            ' tickers exist between ' + start + ' and ' + end

        # filter out stocks that did not exist between |start| and |end|
        self.df = self.df[self.df[self.ticker].isin(tickers)]
        self.df = self.df.reset_index(drop=True)

    def estimate_mean_covariance(self, column):
        ''' Mean and covariance estimation.

        Mean is computed using the natural log

        Various methods to compute the covariance between stocks in |self.df|
        using the |column| price (e.g,. closing) for each day to find the
        return between consecutive days:
            1) self.cov_ml: maximum likelihood covariance estimate
            2) self.cov_sh: covariance estimate with shrinkage
            3) self.cov_lw: Ledoit-Wolf shrinkage estimate
            4) self.cov_oa: oracle approximating shrinkage estimate
        '''
        if self.df is None:
            raise ValueError('No data loaded.')
        elif column not in self.df.columns:
            raise ValueError(column + ' is not a valid database column name.')

        print 'INFO: Computing return percent changes...'
        start_time = time.clock()

        tickers = sorted(list(set(self.df[self.ticker].values)))
        dates = sorted(list(set(self.df[self.date].values)))

        price_dict = {}
        for _, row in self.df.iterrows():
            date_str = str(row[self.date].date())
            price_dict[date_str + row[self.ticker]] = row[column]

        price_list = []
        for date in dates:
            ticker_prices = []
            for ticker in tickers:
                key = str(date)[:DATELEN] + ticker
                if key in price_dict:
                    ticker_prices.append(price_dict[key])
                else:
                    ticker_prices.append(np.nan)
            price_list.append(ticker_prices)

        dfc = pd.DataFrame(price_list).dropna().reset_index(drop=True)
        dfc.columns = tickers

        print 'INFO: Return percent changes computed in ' + \
            str(int((time.clock() - start_time) / 60)) + ' min'

        print 'INFO: Estimating mean returns...'
        start_time = time.clock()

        dfm_log = np.log(dfc / dfc.shift())
        dfm_log = dfm_log.dropna().reset_index(drop=True)

        mean_log_list = [dfm_log[ticker].mean() for ticker in tickers]
        self.mean_log = np.array(mean_log_list)
        print self.mean_log

        dfm_std = (dfc - dfc.shift()) / dfc.shift()
        dfm_std = dfm_std.dropna().reset_index(drop=True)

        mean_std_list = [dfm_std[ticker].mean() for ticker in tickers]
        self.mean_std = np.array(mean_std_list)
        print self.mean_std

        print 'INFO: Mean return vectors computed in ' + \
            str(int(time.clock() - start_time)) + ' sec'

        print 'INFO: Estimating covariance matrices...'
        start_time = time.clock()
        part_time = time.clock()

        dfc = (dfc - dfc.shift()) / dfc.shift()
        dfc = dfc.dropna().reset_index(drop=True)
        x = dfc.values

        ml = EmpiricalCovariance().fit(x)
        self.cov_ml = ml.covariance_
        print 'INFO: maximum-likelihood covariance computed in ' + \
            str(int(time.clock() - part_time)) + ' sec'
        part_time = time.clock()

        print self.cov_ml

        sh = ShrunkCovariance().fit(x)
        self.cov_sh = sh.covariance_
        print 'INFO: shrunk covariance computed in ' + \
            str(int(time.clock() - part_time)) + ' sec'
        part_time = time.clock()

        print self.cov_sh

        lw = LedoitWolf().fit(x)
        self.cov_lw = lw.covariance_
        print 'INFO: Ledoit-Wolf covariance computed in ' + \
            str(int(time.clock() - part_time)) + ' sec'
        part_time = time.clock()

        print self.cov_lw

        oa = OAS().fit(x)
        self.cov_oa = oa.covariance_
        print 'INFO: oracle approximating shrunk covariance computed in ' + \
            str(int(time.clock() - part_time)) + ' sec'
        part_time = time.clock()

        print self.cov_oa

        print 'INFO: Covariance estimators computed in ' + \
            str(int(time.clock() - start_time)) + ' sec'