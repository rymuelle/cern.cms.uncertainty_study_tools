def select_sectors(df, wheel, station):
    return df[(abs(df.wheel)==wheel) & (df.station==station)]
