import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager, rc
from matplotlib.dates import DateFormatter
import os

## windows
font_path = "C:/Windows/Fonts/KoPubDotumMedium.ttf"
font = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams['axes.unicode_minus'] = False
rc('font', family=font)

## mac
# rc('font', family='AppleGothic')
# plt.rcParams['axes.unicode_minus'] = False

size = 11.5
params = {'legend.fontsize': size,
          'axes.labelsize': size * 1.5,
          'axes.titlesize': size * 1.2,
          'xtick.labelsize': size,
          'ytick.labelsize': size,
          'axes.titlepad': 12}
plt.rcParams.update(params)


def dvr_visual(df):
    result = df[df['DVR'] >= 1].groupby('year').first()
    fig, ax = plt.subplots(figsize=(10, 4.7), dpi=150, facecolor="w")
    sns.lineplot(x='year', y='DOY', data=result[result['location'] == 101], marker='o')
    ax.grid(axis="y", which='major', linestyle='--', linewidth=0.5)
    for s in ["left", "right", "top"]:
        ax.spines[s].set_visible(False)

    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(DateFormatter('%j'))

    fig.tight_layout()
    plt.show()


def chill_visual(df, Hr, loc):
    num_area = {'101': '춘천', '119': "수원", '131': '청주', '143': '대구', '156': "광주", '192': "진주"}
    result = df[df['Ca'] >= Hr[loc]].groupby('year').first()
    fig, ax = plt.subplots(figsize=(10, 4.7), dpi=150, facecolor="w")
    sns.lineplot(x='year', y='DOY', data=result[result['location'] == loc], marker='o')
    ax.grid(axis="y", which='major', linestyle='--', linewidth=0.5)
    for s in ["left", "right", "top"]:
        ax.spines[s].set_visible(False)

    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(DateFormatter('%j'))

    ax.set_ylim(90, 130)
    ax.set_title(f'{num_area[str(loc)]} chill')
    fig.tight_layout()
    plt.show()


def all_visual(df, Hr, loc):
    num_area = {'101': '춘천', '119': "수원", '131': '청주', '143': '대구', '156': "광주", '192': "진주"}
    chill_result = df[(df['location'] == int(loc)) & (df['Ca'] >= Hr[loc])].groupby('year').first()
    dvr_result = df[(df['location'] == int(loc)) & (df['DVR'] >= 1)].groupby('year').first()

    fig, ax = plt.subplots(figsize=(10, 4.7), dpi=150, facecolor="w")
    chill_result['month_day'] = pd.to_datetime(chill_result['month_day'], format='%m-%d')
    dvr_result['month_day'] = pd.to_datetime(dvr_result['month_day'], format='%m-%d')

    pastel_colors = sns.color_palette("pastel")
    sns.lineplot(x='year', y='month_day', data=chill_result, marker='o', label='chill model', color=pastel_colors[0], linewidth=3)
    sns.lineplot(x='year', y='month_day', data=dvr_result, marker='o', label='DVR model', color=pastel_colors[1], linewidth=3)

    ax.grid(axis="y", which='major', linestyle='--', linewidth=0.5)
    for s in ["left", "right", "top"]:
        ax.spines[s].set_visible(False)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(DateFormatter('%m-%d'))
    x_labels = df['year'].unique()
    ax.set_xticks(x_labels)
    ax.set_xticklabels(x_labels, rotation=45)
    ax.set_ylim(pd.Timestamp('1900-03-20'), pd.Timestamp('1900-05-10'))

    ax.set_xlabel('')
    ax.set_ylabel('')

    ax.get_legend().set_title('')
    ax.set_title(f'{num_area[str(loc)]} 복숭아 개화 시기 예측')
    fig.tight_layout()

    output_dir_txt = "./output/images/bloom_date"
    if not os.path.exists(output_dir_txt):
        os.makedirs(output_dir_txt)
    plt.savefig(f'{output_dir_txt}/{num_area[str(loc)]}_peach_bloom.png')

def chill_temp(df, Hr, loc):
    num_area = {'101': '춘천', '119': "수원", '131': '청주', '143': '대구', '156': "광주", '192': "진주"}
    df = df[df['location'] == int(loc)]
    df['month_day'] = pd.to_datetime(df['month_day'], format='%m-%d', errors='coerce')
    df = df.dropna(subset=['month_day'])

    df = df[df['month'] < 6]
    chill_result = df[df['Ca'] >= Hr[loc]].groupby('year').first().reset_index()

    chill_late_year = chill_result.sort_values(by='month_day', ascending=False)['year'][:5].tolist()
    chill_early_year = chill_result.sort_values(by='month_day', ascending=True)['year'][:5].tolist()

    def bloom_rank(row):
        if row['year'] in chill_late_year:
            return 'late'
        elif row['year'] in chill_early_year:
            return 'early'
        else:
            return 'mid'

    df['rank'] = df.apply(bloom_rank, axis=1)

    fig, ax = plt.subplots(figsize=(10, 4.7), dpi=150, facecolor="w")

    top5_data = df[df['rank'] == 'late']
    low5_data = df[df['rank'] == 'early']

    sns.lineplot(x='month_day', y='tavg', data=top5_data, color='orange', label='late 5 Years')
    sns.lineplot(x='month_day', y='tavg', data=low5_data, color='blue', label='early 5 Years')

    ax.grid(axis="y", which='major', linestyle='--', linewidth=0.5)
    for s in ["left", "right", "top"]:
        ax.spines[s].set_visible(False)

    ax.xaxis.set_major_formatter(DateFormatter('%m-%d'))
    plt.legend()
    ax.set_xlabel('')
    ax.set_ylabel('Tavg')
    ax.get_legend().set_title('')
    ax.set_title(f'{num_area[str(loc)]}의 개화 시기에 따른 평균온도')
    fig.tight_layout()

    output_dir_txt = "./output/images/tavg"
    if not os.path.exists(output_dir_txt):
        os.makedirs(output_dir_txt)
    plt.savefig(f'{output_dir_txt}/{num_area[str(loc)]}_tavg.png')



def main():
    Hr = {'101': 245, '119': 180.2, '131': 199.2, '143': 277.4, '156': 150, '192': 271}
    df = pd.read_csv('results.csv')
    df['date'] = pd.to_datetime(df['date'])
    df['month_day'] = pd.to_datetime(df['date']).dt.strftime('%m-%d')
    # dvr_visual(df)
    for loc in Hr:
        # chill_visual(df, Hr, loc)
        all_visual(df, Hr, loc)
        chill_temp(df, Hr, loc)


if __name__ == '__main__':
    main()
