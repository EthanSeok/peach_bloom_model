import pandas as pd
import requests
from io import StringIO
from tqdm import tqdm
import numpy as np

start_year = 2001
year_for = 22

def ischill(df, Tc):
    Tn = df['tmin']
    Tx = df['tmax']
    Tm = (Tx + Tn)/2
    if 0 <= Tc <= Tn <= Tx:
        return 0
    elif 0 <= Tn <= Tc <= Tx:
        return -((Tm - Tn) - ((Tx - Tc)**2) / (2 * (Tx - Tn)))
    elif 0 <= Tn <= Tx <= Tc:
        return (-(Tm - Tn))
    elif Tn <= 0 <= Tx <= Tc:
        return -((Tx**2) / (2 * (Tx - Tn)))
    elif Tn <= 0 <= Tc <= Tx:
        return -(Tx**2)/ (2*(Tx-Tn)) - (((Tx - Tc)**2)/(2*(Tx-Tn)))


def isantichill(df, Tc):
    Tn = df['tmin']
    Tx = df['tmax']
    Tm = (Tx + Tn) / 2

    if 0 <= Tc <= Tn <= Tx:
        return (Tm - Tc)
    elif 0 <= Tn <= Tc <= Tx:
        return (Tx - Tc)**2/(2*(Tx - Tn))
    elif 0 <= Tn <= Tx <= Tc:
        return 0
    elif Tn <= 0 <= Tx <= Tc:
        return 0
    elif Tn <= 0 <= Tc <= Tx:
        return (Tx - Tc)**2/(2*(Tx - Tn))


def dvr_e(df):
    C = 0.014
    D = 0.062

    if df['tavg'] >= 5:
        return C * np.exp(D * df['tavg'])
    else:
        return 0


def dvr_model(df, Tc, Hr):
    df = df[df.index >= '01-30']

    ### DVR 모델
    # df['DVRt'] = df.apply(dvr_e, axis=1)
    # df['DVR'] = df['DVRt'].cumsum()
    # print(df[df['month'] == 4])

    ### chill 모델
    df['Cdt'] = df.apply(lambda x: ischill(x, Tc[x['location']]), axis=1)
    df['Cat'] = df.apply(lambda x: isantichill(x, Tc[x['location']]), axis=1)
    df['Cd'] = abs(df['Cdt']).cumsum()
    df['Ca'] = abs(df['Cat']).cumsum()
    # bloom = df[df['Ca'] >= Hr[df['location'][0]]].iloc[0]['DOY']
    print(df[df['Ca'] >= Hr[df['location'][0]]].iloc[0]['DOY'])
    # print(f'만개일: {bloom}')

    return df



def main():
    results = []
    Tc = {'101': 5, '119': 6, '131': 7, '143': 5.2, '156': 8, '192': 5.1}
    Cr = {'101': -110, '119': -73, '131': -95, '143': -130, '156': -74, '192': -148}
    Hr = {'101': 245, '119': 180.2, '131': 199.2, '143': 277.4, '156': 150, '192': 271}

    df_loc = pd.read_csv('data/location.csv')
    for loc in tqdm(df_loc['loc_num']):
        url = f'https://api.taegon.kr/station/{loc}/?sy={start_year}&ey={start_year + year_for}&format=csv'
        response = requests.get(url)
        csv_data = response.content.decode('utf-8')
        df = pd.read_csv(StringIO(csv_data), skipinitialspace=True)

        df = df[['year', 'month', 'day', 'tavg', 'tmax', 'tmin']]
        df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
        df['location'] = str(loc)
        df['DOY'] = df['date'].dt.dayofyear
        for year in range(start_year, start_year + year_for + 1):
            year_df = df[df['year'] == year].copy()  # Create a new DataFrame for each year
            result = dvr_model(year_df, Tc, Hr)
            results.append(result)

    result_df = pd.concat(results, axis=0, ignore_index=False)


if __name__ == '__main__':
    main()
