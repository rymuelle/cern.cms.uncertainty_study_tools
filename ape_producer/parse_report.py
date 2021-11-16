import pandas as pd
import numpy as np
from ape_producer.sign_conventions import sign_matrix

def square_array(np_arr):
    n_entries = len(np_arr)
    dimm = int(n_entries**.5)
    assert dimm ** 2 == n_entries, "Length {} is not square-root-able.".format(n_entries)
    return np_arr.reshape([dimm, dimm])
    
    
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
                                   "status": report.status})
            if report.status != 'PASS': continue
            #DT
            #format covMatrix
            covMatrix = np.array(report.CovMatrix, dtype=float)
            covMatrix = square_array(covMatrix)
            #strip off last three columns and rows
            #In station 1,2,3 are 144 numbers, because there are 12 params, but we want the first six (three): xx, xy, xz, xphix, xphiy, xphiz, A, B, 0, 0, 0, 0; yx, yy, yz... (xx, xy, xphiz, xA, xB, 0, 0, 0, 0, 0, 0, 0, yx, yy...)
            #In station 4 there are 64 numbers, because there are 8 params, but we want the first five (two): xx, xz, xphix, xphiy, xphiz, A, 0, 0; zx, zz, zphix... (xx, xphiz, xA, 0, 0, 0, 0, 0, phizx, phizphiz...)
            covMatrix = covMatrix[:-3,:-3]*sign_matrix("DT", wheel, station, sector)
            dt_minuit_list[-1]['covMatrix'] = covMatrix
        if chamberType == 'CSC':
            chamberType, endcap, station, ring, sector = postal_address
            csc_minuit_list.append({"endcap": endcap, 
                                   "station": station, 
                                   "ring": ring, 
                                   "sector":sector,
                                   "status": report.status})
            if report.status != 'PASS': continue
            #DT
            #format covMatrix
            covMatrix = np.array(report.CovMatrix, dtype=float)
            covMatrix = square_array(covMatrix)
            #You have a 9x9 matrix. You need the first 6 raw, but the forth line is signa_x_residual and you have to skip it, i.e. after the 9x(6+1)=63 elements you are not interested
            covMatrix = covMatrix[:-3,:-3]*sign_matrix("CSC", endcap, station, ring, sector)
            csc_minuit_list[-1]['covMatrix'] = covMatrix
            
    return pd.DataFrame(dt_minuit_list),  pd.DataFrame(csc_minuit_list)
