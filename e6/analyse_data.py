import pandas as pd
import matplotlib.pyplot as plt
import sys

from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd


def main():
    # get data
    filename = sys.argv[1]
    data = pd.read_csv(filename)

    # do anova test
    anova = stats.f_oneway(
        data['qs1'],
        data['qs2'],
        data['qs3'],
        data['qs4'],
        data['qs5'],
        data['merge1'],
        data['partition_sort']
    )

    # do post hoc analysis: Tukey test
    melted_df = pd.melt(data)

    posthoc = pairwise_tukeyhsd(
        melted_df['value'],
        melted_df['variable'],
        alpha=0.05
    )

    print(anova.pvalue)
    print(posthoc)

    fig = posthoc.plot_simultaneous()
    plt.show()


if __name__ == '__main__':
    main()
