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

        self.n = mean.shape[0]

    def solve(self):
        w = Variable(self.n)
        gamma = Parameter(sign='positive')

        ret = self.mean.T * w
        risk = quad_form(w, self.cov)

        # long only portfolio optimization
        prob = Problem(
            Maximize(ret - gamma * risk),
            [
                sum_entries(w) == 1,
                w >= 0])

        # compute trade-off curve
        risk_data = np.zeros(SAMPLES)
        ret_data = np.zeros(SAMPLES)
        gamma_vals = np.logspace(-2, 3, num=SAMPLES)

        print 'INFO: Solving problem for various risk aversion settings...'
        start_time = time.clock()

        for i in range(SAMPLES):
            gamma.value = gamma_vals[i]
            prob.solve(solver=SCS, verbose=True, use_indirect=True)
            risk_data[i] = sqrt(risk).value
            ret_data[i] = ret.value

        print 'INFO: Finished solving problems in about ' + \
            str(int((time.clock() - start_time) / 60)) + ' min'

        markers_on = [3, 7]

        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.plot(risk_data, ret_data, 'g-')

        for marker in markers_on:
            plt.plot(risk_data[marker], ret_data[marker], 'bs')
            ax.annotate(
                r"$\gamma = %.2f$" % gamma_vals[marker],
                xy=(risk_data[marker]+.08, ret_data[marker]-.03))

        for i in range(self.n):
            plt.plot(sqrt(self.cov[i,i]).value, self.mean[i], 'ro')

        plt.xlabel('Standard deviation')
        plt.ylabel('Return')

    def show(self):
        plt.show()
