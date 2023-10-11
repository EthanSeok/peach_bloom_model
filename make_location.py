import pandas as pd


def main():
    area = ['춘천', '청주', '광주', '수원', '대구', '진주']
    # 관측지점번호: https://data.kma.go.kr/tmeta/stn/selectStnList.do
    df = pd.read_csv('data/META_관측지점정보_20230925191239.csv', encoding='cp949')
    df = df[df['지점명'].isin(area)]
    df = df[['지점', '지점명', '위도', '경도']].drop_duplicates(['지점'])
    df.columns = ['loc_num', 'loc_name', 'lat', 'long']
    df.to_csv('./data/location.csv', index=False, encoding='utf-8-sig')


if __name__ == '__main__':
    main()