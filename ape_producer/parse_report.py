import pandas as pd
import numpy as np
from ape_producer.sign_conventions import sign_matrix

def square_array(np_arr):
    n_entries = len(np_arr)
    dimm = int(n_entries**.5)
    assert dimm ** 2 == n_entries, "Length {} is not square-root-able.".format(n_entries)
    return np_arr.reshape([dimm, dimm])
alignables = ['x','y','z','phix', 'phiy', 'phiz']

def safe_value(chamb, key):
    # this function deals with the fact that row 4 has a nonetype dimension: y
    dim_values = []
    for dim in alignables:
        dim_value = chamb.__dict__['delta{}'.format(dim)]
        if dim_value is not None:
            dim_values.append(dim_value.__dict__[key])
        else: dim_values.append(-9999)
    return np.array(dim_values)

def get_chamb_unc(chamb, calc=False):
    import uncertainties
    if not calc:
        error = safe_value(chamb, 'error')
    #for comparision, here is how to calculate it
    if calc:
        nominal = safe_value(chamb, 'value')
        cov = square_array(np.array(chamb.CovMatrix, dtype=float))[0:6,0:6]
        unc = uncertainties.correlated_values(nominal,cov)
        error = list(map(lambda x: x.std_dev, unc))
    return np.array(error)

def make_cov_objects(reports, debug=False):
    dt_minuit_list = []
    csc_minuit_list = []
    for report in reports:
        if debug: print(report)
        postal_address = report.postal_address
        chamberType = postal_address[0]
        status = report.status
        #only take passing chambers:
        if chamberType == 'DT':
            chamberType, wheel, station, sector = postal_address
            dt_minuit_list.append({"wheel": wheel, 
                                   "station": station, 
                                   "sector": sector, 
                                   "status": report.status,
                                  "nMuons": report.posNum})
            if report.status != 'PASS': continue
            #DT
            #format covMatrix
            covMatrix = np.array(report.CovMatrix, dtype=float)
            covMatrix = square_array(covMatrix)
            error = get_chamb_unc(report)
            #strip off last three columns and rows
            #In station 1,2,3 are 144 numbers, because there are 12 params, but we want the first six (three): xx, xy, xz, xphix, xphiy, xphiz, A, B, 0, 0, 0, 0; yx, yy, yz... (xx, xy, xphiz, xA, xB, 0, 0, 0, 0, 0, 0, 0, yx, yy...)
            #In station 4 there are 64 numbers, because there are 8 params, but we want the first five (two): xx, xz, xphix, xphiy, xphiz, A, 0, 0; zx, zz, zphix... (xx, xphiz, xA, 0, 0, 0, 0, 0, phizx, phizphiz...)
            covMatrix = covMatrix[0:6,0:6]*sign_matrix("DT", wheel, station, sector)
            dt_minuit_list[-1]['covMatrix'] = covMatrix
            dt_minuit_list[-1]['error'] = error
        if chamberType == 'CSC':
            chamberType, endcap, station, ring, sector = postal_address
            csc_minuit_list.append({"endcap": endcap, 
                                   "station": station, 
                                   "ring": ring, 
                                   "sector":sector,
                                   "status": report.status,
                                   "nMuons": report.posNum})
            if report.status != 'PASS': continue
            #DT
            #format covMatrix
            covMatrix = np.array(report.CovMatrix, dtype=float)
            covMatrix = square_array(covMatrix)
            error = get_chamb_unc(report, calc=True)
            #You have a 9x9 matrix. You need the first 6 raw, but the forth line is signa_x_residual and you have to skip it, i.e. after the 9x(6+1)=63 elements you are not interested
            covMatrix = covMatrix[0:6,0:6]*sign_matrix("CSC", endcap, station, ring, sector)
            csc_minuit_list[-1]['covMatrix'] = covMatrix
            csc_minuit_list[-1]['error'] = error
            
    return pd.DataFrame(dt_minuit_list),  pd.DataFrame(csc_minuit_list)
