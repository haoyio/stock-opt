from estimate.constants import *

class Estimator(object):
    ''' Wrapper for loading stock price data and estimating covariance. '''
    def __init__(self, ticker_column, date_column):
        self.ticker = ticker_column # column name for tickers; e.g., 'ticker'
        self.date = date_column # column name for timestamps; e.g., 'date'

        self.df = None # stock price dataframe
        self.returns = None # mean return estimate

        self.ml = None # maximum likelihood covariance estimate
        self.sh = None # covariance estimate with shrinkage
        self.lw = None # Ledoit-Wolf shrinkage estimate
        self.oa = None # oracle approximating shrinkage estimate

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

        print 'INFO: a total of ' + str(len(tickers)) + \
            ' tickers exist between ' + start + ' and ' + end

        # filter out stocks that did not exist between |start| and |end|
        self.df = self.df[self.df[self.ticker].isin(tickers)]
        self.df = self.df.reset_index(drop=True)

    def estimate_mean(self, column):
        ''' Mean estimation. '''
        pass

    def estimate_covariance(self, column):
        ''' Covariance estimation.

        Various methods to compute the covariance between stocks in |self.df|
        using the |column| price (e.g,. closing) for each day to find the
        return between consecutive days:
            1) self.ml: maximum likelihood covariance estimate
            2) self.sh: covariance estimate with shrinkage
            3) self.lw: Ledoit-Wolf shrinkage estimate
            4) self.oa: oracle approximating shrinkage estimate
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

        print 'INFO: Estimating covariance matrices...'
        start_time = time.clock()
        part_time = time.clock()

        x = dfc.values

        self.ml = empirical_covariance(x)
        print '\tmaximum-likelihood covariance computed in ' + \
            str(int(time.clock() - part_time)) + ' sec'
        part_time = time.clock()

        sh = ShrunkCovariance().fit(x)
        self.sh = sh.covariance_
        print '\tshrunk covariance computed in ' + \
            str(int(time.clock() - part_time)) + ' sec'
        part_time = time.clock()

        lw = LedoitWolf().fit(x)
        self.lw = lw.covariance_
        print '\tLedoit-Wolf covariance computed in ' + \
            str(int(time.clock() - part_time)) + ' sec'
        part_time = time.clock()

        oa = OAS().fit(x)
        self.oa = oa.covariance_
        print '\toracle approximating shrunk covariance computed in ' + \
            str(int(time.clock() - part_time)) + ' sec'
        part_time = time.clock()

        print self.ml
        print self.sh
        print self.lw
        print self.oa

        print 'INFO: Covariance estimators computed in ' + \
            str(int(time.clock() - start_time)) + ' sec'