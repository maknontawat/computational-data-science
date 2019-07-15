import sys

from pyspark.sql import SparkSession, functions, types

spark = SparkSession.builder.appName('reddit averages').getOrCreate()
spark.sparkContext.setLogLevel('WARN')

assert sys.version_info >= (3, 5)  # make sure we have Python 3.5+
assert spark.version >= '2.3'      # make sure we have Spark 2.3+


pages_schema = types.StructType([
    types.StructField('lang', types.StringType()),
    types.StructField('title', types.StringType()),
    types.StructField('views', types.LongType()),
    types.StructField('bytes', types.LongType()),
])


def to_hour(path):
    path = path[path.rfind('pagecounts-'):]
    path = path[path.index('-') + 1:-4]
    return path


def main(in_directory, out_directory):
    # fixes timestamp column
    path_to_hour = functions.udf(
        lambda z: to_hour(z),
        returnType=types.StringType()
    )

    # creates spark dataframe
    pages = spark.read.csv(in_directory, sep=" ", schema=pages_schema)

    # applies filters
    pages = pages.filter(pages['lang'] == 'en')
    pages = pages.filter(pages['title'] != 'Main_Page')
    pages = pages.filter(pages['title'].startswith('Special:') == False)

    # add timestamp column
    pages = pages.withColumn(
        'timestamp',
        path_to_hour(functions.input_file_name())
    )

    # cache the dataframe
    pages = pages.cache()

    # find the largest number of page views in each hour
    max_views_per_hr = pages.groupBy('timestamp').agg(functions.max('views'))
    max_views_per_hr = max_views_per_hr.withColumnRenamed('timestamp', 'ts')

    # join to get page name of most visited page
    join_where = [
        (pages['views'] == max_views_per_hr['max(views)']) &
        (pages['timestamp'] == max_views_per_hr['ts'])
    ]

    # eliminate duplicate columns
    pages = pages.join(max_views_per_hr, join_where, 'right_outer')
    pages = pages.select(
        max_views_per_hr['ts'],
        pages['title'],
        max_views_per_hr['max(views)']
    )

    # sort by timestamp, title and then views
    pages = pages.sort('timestamp', 'title', 'views')

    # write to output
    pages.coalesce(1).write.csv(
        out_directory + '-wiki',
        mode='overwrite'
    )


if __name__ == '__main__':
    in_directory = sys.argv[1]
    out_directory = sys.argv[2]
    main(in_directory, out_directory)
