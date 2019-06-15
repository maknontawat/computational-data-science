from scipy import stats

import sys
import pandas as pd
import numpy as np


OUTPUT_TEMPLATE = (
    "Initial (invalid) T-test p-value: {initial_ttest_p:.3g}\n"
    "Original data normality p-values: {initial_weekday_normality_p:.3g} {initial_weekend_normality_p:.3g}\n"
    "Original data equal-variance p-value: {initial_levene_p:.3g}\n"
    "Transformed data normality p-values: {transformed_weekday_normality_p:.3g} {transformed_weekend_normality_p:.3g}\n"
    "Transformed data equal-variance p-value: {transformed_levene_p:.3g}\n"
    "Weekly data normality p-values: {weekly_weekday_normality_p:.3g} {weekly_weekend_normality_p:.3g}\n"
    "Weekly data equal-variance p-value: {weekly_levene_p:.3g}\n"
    "Weekly T-test p-value: {weekly_ttest_p:.3g}\n"
    "Mann–Whitney U-test p-value: {utest_p:.3g}"
)


def is_weekend(date):
    day = date.weekday()
    return day == 5 or day == 6


def is_weekday(date):
    return not is_weekend(date)


def apply_filters(data):
    """
    we will look only at values:
    (1) in 2012 and 2013, and
    (2) in the /r/canada subreddit

    """
    data = data[
        (data['subreddit'] == 'canada') &
        (
            (data['year'] == 2012) |
            (data['year'] == 2013)
        )
    ]

    return data


def process_data(data):
    data['year'] = data['date'].apply(lambda x: x.year)

    data = apply_filters(data)

    # don't need the year col anymore
    del data['year']

    # return (weekends, weekdays)
    return (
        data[data['date'].apply(is_weekend)],
        data[data['date'].apply(is_weekday)]
    )


def get_weekly_mean(data):
    data['year'] = data['date'].apply(lambda x: x.isocalendar()[0])
    data['week'] = data['date'].apply(lambda x: x.isocalendar()[1])

    return data.groupby(['year', 'week']).mean()


def main():
    # preprare data
    reddit_counts = pd.read_json(sys.argv[1], lines=True)
    weekends, weekdays = process_data(reddit_counts)
    weekend_comments = weekends['comment_count']
    weekday_comments = weekdays['comment_count']

    # Do normal and levene test on untransformed data
    initial_ttest = stats.ttest_ind(weekend_comments, weekday_comments)
    initial_weekday_normality = stats.normaltest(weekday_comments)
    initial_weekend_normality = stats.normaltest(weekend_comments)
    initial_levene = stats.levene(weekend_comments, weekday_comments)

    # Fix 1: transforming data
    weekends_transf = np.sqrt(weekend_comments)
    weekdays_transf = np.sqrt(weekday_comments)
    transformed_weekday_normality = stats.normaltest(weekdays_transf)
    transformed_weekend_normality = stats.normaltest(weekends_transf)
    transformed_levene = stats.levene(weekends_transf, weekdays_transf)

    # Fix 2: the Central Limit Theorem
    weekly_weekday = get_weekly_mean(weekdays)['comment_count']
    weekly_weekend = get_weekly_mean(weekends)['comment_count']
    weekly_weekday_normality = stats.normaltest(weekly_weekday)
    weekly_weekend_normality = stats.normaltest(weekly_weekend)
    weekly_levene = stats.levene(weekly_weekend, weekly_weekday)
    weekly_ttest = stats.ttest_ind(weekly_weekend, weekly_weekday)

    # Fix 3: a non-parametric test
    mwutest = stats.mannwhitneyu(
        weekend_comments,
        weekday_comments,
        alternative='two-sided'
    )

    print(OUTPUT_TEMPLATE.format(
        initial_ttest_p=initial_ttest.pvalue,
        initial_weekday_normality_p=initial_weekday_normality.pvalue,
        initial_weekend_normality_p=initial_weekend_normality.pvalue,
        initial_levene_p=initial_levene.pvalue,
        transformed_weekday_normality_p=transformed_weekday_normality.pvalue,
        transformed_weekend_normality_p=transformed_weekend_normality.pvalue,
        transformed_levene_p=transformed_levene.pvalue,
        weekly_weekday_normality_p=weekly_weekday_normality.pvalue,
        weekly_weekend_normality_p=weekly_weekend_normality.pvalue,
        weekly_levene_p=weekly_levene.pvalue,
        weekly_ttest_p=weekly_ttest.pvalue,
        utest_p=mwutest.pvalue,
    ))


if __name__ == '__main__':
    main()
