from difflib import get_close_matches

import sys
import pandas as pd


def get_movies(file):
    def strip(x):
        return x.strip()

    data = map(strip, open(file).readlines())
    return list(data)


def get_movie_ratings(file):
    return pd.read_csv(file)


def title_entity_res(crct_titles, movies):
    titles = movies['title']

    # do entity resolution
    entity_res = titles.apply(lambda x: get_close_matches(x, crct_titles, n=1))

    # align mis-typed titles with correct ones
    movies['correct-title'] = entity_res.apply(
        lambda x: x[0] if len(x) != 0 else None
    )

    # drop garbage movies
    movies = movies.dropna(subset=['correct-title'])

    # sort movies by title
    movies = movies.sort_values(by=['correct-title'])

    # drop the wrong titles column
    del movies['title']

    # rename correct-title to just title
    movies.rename(columns={'correct-title': 'title'}, inplace=True)

    return movies


def get_avg_ratings(movies):
    avg_ratings = movies.groupby('title').mean()
    avg_ratings['rating'] = avg_ratings['rating'].apply(lambda x: round(x, 2))

    return avg_ratings


def main():
    movie_list_file = sys.argv[1]
    movie_ratings_file = sys.argv[2]
    output = sys.argv[3]

    correct_titles = get_movies(movie_list_file)
    movies = get_movie_ratings(movie_ratings_file)

    df = title_entity_res(correct_titles, movies)

    df_avg_ratings = get_avg_ratings(df)
    df_avg_ratings.to_csv(path_or_buf=output)

    return


if __name__ == "__main__":
    main()
