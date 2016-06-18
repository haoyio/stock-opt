from estimate.constants import *

class Estimator(object):
    ''' Wrapper for loading stock price data and estimating covariance. '''
    def __init__(self):
        self.df = None # stock price dataframe
        self.returns = None # mean return estimate
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