import sys
import string
import re

from pyspark.sql import SparkSession, functions, types

spark = SparkSession.builder.appName('word count').getOrCreate()

assert sys.version_info >= (3, 4)  # make sure we have Python 3.4+
assert spark.version >= '2.1'  # make sure we have Spark 2.1+


def main(in_directory, out_directory):
    # 1. Read lines from the files with spark.read.text.
    lines = spark.read.text(in_directory).cache()

    # 2. Split the lines into words with the regular expression below.

    # regex that matches spaces and/or punctuation
    wordbreak = r'[%s\s]+' % (re.escape(string.punctuation),)
    words = lines\
        .select(functions.split(lines['value'], wordbreak).alias('value'))\
        .cache()

    words = words.select(functions.explode(words['value']).alias('value'))
    words = words.select(functions.lower(words['value']).alias('word'))

    # 3. Count the number of times each word occurs.
    word_count = words.groupBy('word').count().cache()

    # 4. Sort by decreasing count (i.e. frequent words first) and alphabetically if there's a tie.
    word_count = word_count.sort(functions.desc('count')).cache()

    # 5. Notice that there are likely empty strings being counted: remove them from the output.
    word_count = word_count.filter(word_count['word'] != '')

    # 6. Write results as CSV files with the word in the first column,
    # and count in the second (uncompressed: they aren't big enough to worry about).
    word_count.coalesce(1).write.csv(
        out_directory + '-wordcount',
        mode='overwrite'
    )


if __name__ == '__main__':
    in_directory = sys.argv[1]
    out_directory = sys.argv[2]
    main(in_directory, out_directory)
