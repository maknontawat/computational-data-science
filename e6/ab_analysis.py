import sys
import pandas as pd
import numpy as np

from scipy import stats

OUTPUT_TEMPLATE = (
    '"Did more/less users use the search feature?" p-value: {more_users_p:.3g}\n'
    '"Did users search more/less?" p-value: {more_searches_p:.3g}\n'
    '"Did more/less instructors use the search feature?" p-value: {more_instr_p:.3g}\n'
    '"Did instructors search more/less?" p-value: {more_instr_searches_p:.3g}'
)


def get_data(file):
    """
    Reads data from .json file.
    """
    return pd.read_json(file, orient='records', lines=True)


# implemented from:
# https://stackoverflow.com/questions/20458498/python-splitting-strings-into-even-and-odd-two-dataframes-efficiently
def odd_even_uid(data):
    """
    Separates both odd and even uid records.
    """
    is_even = data['uid'].astype(int) % 2 == 0
    return data[~is_even],  data[is_even]


def instrs_only(data):
    """
    Filters out non-instructor records.
    """
    return data[data['is_instructor']]


def searched_once(data):
    """
    Returns records with search_count > 0.
    """
    return data[data['search_count'] > 0]


def never_searched(data):
    """
    Returns records with search_count exactly zero.
    """
    return data[data['search_count'] == 0]


def chi_square_test(odd_uid, even_uid):
    """
    Returns a pvalue from a Chi-square test of independence of
    variables in a contingency table.
    """
    so_even_uid = searched_once(even_uid)
    ns_even_uid = never_searched(even_uid)
    so_odd_uid = searched_once(odd_uid)
    ns_odd_uid = never_searched(odd_uid)

    contingency_table = [
        [
            so_even_uid.shape[0],
            ns_even_uid.shape[0]
        ],
        [
            so_odd_uid.shape[0],
            ns_odd_uid.shape[0]
        ]
    ]

    _, p, _, _ = stats.chi2_contingency(contingency_table)

    return p


def main():
    searchdata_file = sys.argv[1]
    searchdata = get_data(searchdata_file)

    # make two groups
    # odd_uid: feature enabled
    # even_uid: feature disabled
    odd_uid, even_uid = odd_even_uid(searchdata)

    # Did more/less users use the search feature?
    users_srchs_p = chi_square_test(odd_uid, even_uid)

    # Did users search more/less?
    mwutest_searches_p = stats.mannwhitneyu(
        odd_uid['search_count'],
        even_uid['search_count'],
        alternative='two-sided').pvalue

    # Repeating tests for instructors only
    instrs = instrs_only(searchdata)

    # make two groups
    odd_instrs, even_instrs = odd_even_uid(instrs)

    # Did more/less instr users use the search feature?
    instrs_srchs_p = chi_square_test(odd_instrs, even_instrs)

    # Did instr users search more/less?
    mwutest_instr_searches_p = stats.mannwhitneyu(
        odd_instrs['search_count'],
        even_instrs['search_count'],
        alternative='two-sided').pvalue

    # Output
    print(OUTPUT_TEMPLATE.format(
        more_users_p=users_srchs_p,
        more_searches_p=mwutest_searches_p,
        more_instr_p=instrs_srchs_p,
        more_instr_searches_p=mwutest_instr_searches_p,
    ))


if __name__ == '__main__':
    main()
