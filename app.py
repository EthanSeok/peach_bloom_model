import pandas as pd
import requests
from io import StringIO
import streamlit as st
import os
import numpy as np
import plotly.graph_objs as go
import model
import visualize
import plotly.express as px

year = 2001
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


def dvr_e(df, C, D):
    if df['tavg'] >= 5:
        return C * np.exp(D * df['tavg'])
    else:
        return 0


def models(df, Tc, Hr, C, D):
    df = df.reset_index()
    df = df[(df['date'].dt.month > 1) | ((df['date'].dt.month == 1) & (df['date'].dt.day >= 30))]
    df['Cdt'] = df.apply(lambda x: ischill(x, Tc[x['location']]), axis=1)
    df['Cat'] = df.apply(lambda x: isantichill(x, Tc[x['location']]), axis=1)
    df['Cd'] = abs(df['Cdt']).cumsum()
    df['Ca'] = abs(df['Cat']).cumsum()
    df['DVRi'] = df.apply(lambda x: dvr_e(x, C[x['location']], D[x['location']]), axis=1)
    df['DVR'] = df['DVRi'].cumsum()

    bloom_chill_date = df[df['Ca'] >= Hr[df['location'].iloc[0]]].iloc[0]['date']
    bloom_chill = bloom_chill_date.strftime('%m월%d일')
    bloom_dvr = df[df['DVR'] >= 1].iloc[0]['date'].strftime('%m월%d일')

    return bloom_chill, bloom_dvr

def intro():
    import streamlit as st

    st.write("# 🍑 복숭아 개화 모델")
    st.sidebar.success("Select a demo above.")

    st.markdown(
        """
        2023-2학기 스마트농업프로그래밍에서 진행한 복숭아 개화시기 예측모델입니다. 더 많은 기능은 
        
        
        **👈 옆에 사이드바에서 확인하세요!**

        
        
        ### 복숭화 개화 모델 종류

        - 본 프로그램에서 사용한 복숭아 개화 모델은 CD 모델(Chill day model)과 DVR 모델(Development Rate model) 두개 입니다.
        
        - CD 모델은 일의 최고 및 최저기온을 이용해 기준온도(threshold temperature, Tc)로부터 유효한 온도범위에 따라 가중치를 달리하 여 내생휴면해제 이전까지는 냉각량(chill unit), 그 이 후는 가온량(heat unit)으로 표현하여 
        고온 요구도를 넘는 날을 기점으로 만개기로 간주합니다.
        
        - DVR 모델은 온도에 따른 과수의 발육 속도를 계산하여 적산함으로써 만개기를 예측하는 모델입니다. 여기서 온도는 5°C 이상의 평균 기온을 기록한 날만 반영합니다.
        
        
        ![image](https://github.com/EthanSeok/APSIM_Wheat_Scenario/assets/93086581/59a79943-e682-4278-8b76-f6e38db32158)

        ![image](https://github.com/EthanSeok/APSIM_Wheat_Scenario/assets/93086581/8d042ecb-7c18-4f5b-abb6-3add02904dba)
        
        
        
        ### 참고 문헌

        - Chun, J. A., Kang, K., Kim, D., Han, H. H., & Son, I. C. (2017). Prediction of full blooming dates of five peach cultivars (Prunus persica) using temperature-based models. Scientia Horticulturae, 220, 250-258.
    """
    )


def get_marker_color_doy(value, min_value, max_value):
    colorscale = ["blue", "red"]
    normalized_value = (value - min_value) / (max_value - min_value)
    color_index = int(normalized_value * (len(colorscale) - 1))
    return colorscale[color_index]

def mapping_demo():
    df = pd.read_csv('data/location.csv')
    df2 = pd.read_csv('output/results.csv')
    Hr = {'101': 245, '119': 180.2, '131': 199.2, '143': 277.4, '156': 150, '192': 271}

    st.markdown("## 복숭아 개화 지도", unsafe_allow_html=True)

    cd_result = []
    dvr_result = []
    for loc in df2['location'].unique():
        cd_result.append(df2[(df2['location'] == int(loc)) & (df2['Ca'] >= Hr[str(loc)])].groupby('year').first().reset_index())
        dvr_result.append(df2[(df2['location'] == int(loc)) & (df2['DVR'] >= 1)].groupby('year').first().reset_index())

    cd_result = pd.concat(cd_result, axis=0, ignore_index=False)
    dvr_result = pd.concat(dvr_result, axis=0, ignore_index=False)

    cd_result['lat'] = cd_result['location'].map(df.set_index('loc_num')['lat'])
    cd_result['long'] = cd_result['location'].map(df.set_index('loc_num')['long'])
    dvr_result['lat'] = dvr_result['location'].map(df.set_index('loc_num')['lat'])
    dvr_result['long'] = dvr_result['location'].map(df.set_index('loc_num')['long'])

    selected_df = st.radio("모델 선택", ["cd_result", "dvr_result"])
    selected_year = st.selectbox("연도 선택", df2['year'].unique())

    st.markdown("색이 진할 수록 개화 늦음", unsafe_allow_html=True)

    if selected_df == "cd_result":
        result_df = cd_result
    else:
        result_df = dvr_result

    filtered_df = result_df[result_df['year'] == selected_year]
    filtered_df['lat'] = filtered_df['location'].map(df.set_index('loc_num')['lat'])
    filtered_df['long'] = filtered_df['location'].map(df.set_index('loc_num')['long'])

    color_scale = px.colors.sequential.YlOrRd

    min_value = filtered_df['DOY'].min()
    max_value = filtered_df['DOY'].max()
    normalized_doy = (filtered_df['DOY'] - min_value) / (max_value - min_value)

    colors = [color_scale[int(value * (len(color_scale) - 1))] for value in normalized_doy]
    trace = go.Scattermapbox(
        lat=filtered_df['lat'],
        lon=filtered_df['long'],
        mode="markers",
        marker={"size": 15, "color": colors, "colorscale": color_scale},
        text=filtered_df['location'],
    )

    layout = go.Layout(
        mapbox_style="carto-positron",
        mapbox_center={"lat": df['lat'].mean(), "lon": df['long'].mean()},
        mapbox_zoom=5.5,
        width=450,
        height=700
    )

    fig = go.Figure(data=[trace], layout=layout)

    st.plotly_chart(fig)


def plotting_demo():
    st.title('복숭아 개화 시기 예측')
    select_year = st.number_input('연도 선택', min_value=2001, max_value=2023, value=2022)
    num_area = {'101': '춘천', '119': "수원", '131': '청주', '143': '대구', '156': "광주", '192': "진주"}
    area_num = {'춘천': '101', '수원': "119", '청주': '131', '대구': '143', '광주': "156", '진주': "192"}
    C = {'101': 0.011, '119': 0.007, '131': 0.002, '143': 0.006, '156': 0.017, '192': 0.020}
    D = {'101': 0.093, '119': 0.138, '131': 0.261, '143': 0.129, '156': 0.043, '192': 0.028}
    Tc = {'101': 5, '119': 6, '131': 7, '143': 5.2, '156': 8, '192': 5.1}
    Cr = {'101': -110, '119': -73, '131': -95, '143': -130, '156': -74, '192': -148}
    Hr = {'101': 245, '119': 180.2, '131': 199.2, '143': 277.4, '156': 150, '192': 271}

    loc = st.selectbox('측후소 선택', list(num_area.values()))
    location = area_num[loc]
    if st.button('CD 모델 실행'):
        st.write(f'{loc}지역의 {select_year}년의 복숭화 개화 모델 실행중...')
        url = f'https://api.taegon.kr/station/{location}/?sy={year}&ey={year + year_for}&format=csv'
        response = requests.get(url)
        csv_data = response.content.decode('utf-8')
        df = pd.read_csv(StringIO(csv_data), skipinitialspace=True)

        df = df[df['year'] == select_year]
        df = df[['year', 'month', 'day', 'tavg', 'tmax', 'tmin', 'rainfall', 'snow']]
        df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
        df['location'] = str(location)
        df['DOY'] = df['date'].dt.dayofyear
        # model.main()
        # visualize.main()
        df.set_index('date', inplace=True)
        st.write(f'{select_year}년 {loc}의 복숭아의 예상 개화일은 {models(df, Tc, Hr, C, D)[0]}입니다.')

    if st.button('DVR 모델 실행'):
        st.write(f'{loc}지역의 {select_year}년의 복숭화 개화 모델 실행중...')
        url = f'https://api.taegon.kr/station/{location}/?sy={year}&ey={year + year_for}&format=csv'
        response = requests.get(url)
        csv_data = response.content.decode('utf-8')
        df = pd.read_csv(StringIO(csv_data), skipinitialspace=True)

        df = df[df['year'] == select_year]
        df = df[['year', 'month', 'day', 'tavg', 'tmax', 'tmin']]
        df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
        df['location'] = str(location)
        df['DOY'] = df['date'].dt.dayofyear
        # model.main()
        df.set_index('date', inplace=True)
        st.write(f'{select_year}년 {loc}의 복숭아의 예상 개화일은 {models(df, Tc, Hr, C, D)[1]}입니다.')

def result_image():
    loc_list = ['춘천', '수원', '청주', '대구', '광주', '진주']
    st.markdown("## 과거 복숭아 개화 결과", unsafe_allow_html=True)
    selected_loc = st.selectbox("지역을 선택하세요.", loc_list)

    if selected_loc:
        image_folder = "output/images/bloom_date"
        selected_image = f"{selected_loc}_peach_bloom.png"
        image_path = os.path.join(image_folder, selected_image)
        st.image(image_path, caption=selected_image, use_column_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("## 과거 복숭아 재배지 평균 기온", unsafe_allow_html=True)
        temp_folder = "output/images/tavg"
        selected_image = f"{selected_loc}_tavg.png"
        image_path = os.path.join(temp_folder, selected_image)
        st.image(image_path, caption=selected_image, use_column_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("## 과거 복숭아 재배지 강수량", unsafe_allow_html=True)
        temp_folder = "output/images/precipitation"
        selected_image = f"{selected_loc}_precipitation.png"
        image_path = os.path.join(temp_folder, selected_image)
        st.image(image_path, caption=selected_image, use_column_width=True)


page_names_to_funcs = {
    "메인": intro,
    "복숭아 개화 모델": plotting_demo,
    "복숭아 개화 지도": mapping_demo,
    "과거 복숭아 개화 결과 및 분석": result_image
}

demo_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()