import time
import numpy as np
import pandas as pd
import sys

from implementations import all_implementations


def generate_df():
    n_arrs = 50
    arr_size = 15000

    groups = ['qs1', 'qs2', 'qs3', 'qs4', 'qs5', 'merge1', 'partition_sort']
    df = pd.DataFrame(
        columns=groups,
        index=np.arange(n_arrs)
    )

    for i in range(n_arrs):
        arr = np.random.randint(-sys.maxsize, sys.maxsize, size=arr_size)
        for sort in all_implementations:
            st = time.time()
            res = sort(arr)
            en = time.time()
            diff = en - st
            df.iloc[i][sort.__name__] = diff

    return df


def main():
    generate_df().to_csv('data.csv', index=False)


if __name__ == '__main__':
    main()
