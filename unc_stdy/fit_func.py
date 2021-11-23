def standard_error(n, sigma):
    '''standard error of the mean'''
    return sigma / n ** .5

def std_err_sys(n, sigma, sys):
    '''Calculates a broadening effect on the standard error due to a normal systematic'''
    return (standard_error(n,sigma) ** 2 + sys ** 2) ** 0.5
