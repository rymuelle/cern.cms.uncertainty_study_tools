import pandas as pd

#template df for wheels and stations
wheel_stations_df = pd.DataFrame([{"wheel": w,"station": s} for w in [0,1,2] for s in [1,2,3,4]])
