import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def get_views_data(filename):
    return pd.read_csv(
        filename,
        sep=' ',
        header=None,
        index_col=1,
        names=['lang', 'page', 'views', 'bytes']
    )


def draw_plots(df1, df2):
    fig = plt.figure(figsize=(15, 7))

    plot_dist_of_views(fig, df1)
    plot_daily_views(fig, df1, df2)

    plt.savefig('wikipedia.png')


def plot_dist_of_views(fig, df1):
    # sort df1 by views
    sort_by_views = df1.sort_values(by=['views'])

    # plots distribution of views
    fig.add_subplot(1, 2, 1)
    plt.title('Popularity Distribution')
    plt.xlabel('Rank')
    plt.ylabel('Views')
    plt.plot(sort_by_views['views'].values)


def plot_daily_views(fig, df1, df2):
    # gets the two series into the same DataFrame
    views_df = pd.DataFrame()
    views_df['day1'] = df1['views']
    views_df['day2'] = df2['views']

    # plots daily views
    fig.add_subplot(1, 2, 2)
    plt.title('Daily Correlation')
    plt.xlabel('Day 1 views')
    plt.ylabel('Day 2 views')
    plt.xscale('log')
    plt.yscale('log')
    plt.scatter(views_df['day1'], views_df['day2'], c='b')


def main():
    filename1 = sys.argv[1]
    filename2 = sys.argv[2]

    dataset1 = get_views_data(filename1)
    dataset2 = get_views_data(filename2)

    df1 = pd.DataFrame(dataset1)
    df2 = pd.DataFrame(dataset2)

    draw_plots(df1, df2)


if __name__ == '__main__':
    main()
