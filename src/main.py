from constants import *

def get_data(
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
    df = pd.read_csv(filename, compression=compression, parse_dates=parse_dates)
    df.columns = columns
    print 'INFO: ' + filename + ' loaded in ' + \
        str(int(time.clock() - start_time)) + ' sec'
    return df

if __name__ == '__main__':
    df = get_data(DATABASE, FILENAME, COMPRESSION, COLUMNS, PARSE_DATES)

