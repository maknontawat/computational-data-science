import sys
import math
import re

from pyspark.sql import SparkSession, functions, types, Row

spark = SparkSession.builder.appName('correlate logs').getOrCreate()
spark.sparkContext.setLogLevel('WARN')

assert sys.version_info >= (3, 5)  # make sure we have Python 3.5+
assert spark.version >= '2.3'  # make sure we have Spark 2.3+

line_re = re.compile(
    r"^(\S+) - - \[\S+ [+-]\d+\] \"[A-Z]+ \S+ HTTP/\d\.\d\" \d+ (\d+)$"
)


def line_to_row(line):
    """
    Take a logfile line and return a Row object with hostname and bytes transferred.
    Return None if regex doesn't match.
    """
    m = line_re.match(line)
    if m:
        return Row(hostname=m.group(1), num_bytes=m.group(2))
    else:
        return None


def not_none(row):
    """
    Is this None? Hint: .filter() with it.
    """
    return row is not None


def create_row_rdd(in_directory):
    log_lines = spark.sparkContext.textFile(in_directory)

    # TODO: return an RDD of Row() objects
    rows = log_lines.map(line_to_row)
    rows = rows.filter(not_none)

    return rows


def main(in_directory):
    logs = spark.createDataFrame(create_row_rdd(in_directory)).cache()

    # TODO: calculate r.
    num_requests_per_host = logs\
        .groupBy('hostname')\
        .agg(functions.count('hostname').alias('num_requests'))

    total_bytes_per_host = logs\
        .groupBy('hostname')\
        .agg(functions.sum('num_bytes').alias('sum_request_bytes'))

    join_on = ['hostname']

    logs = num_requests_per_host.join(total_bytes_per_host, join_on)
    logs = logs.select(
        logs['num_requests'].alias('xi'),
        logs['sum_request_bytes'].alias('yi')
    )
    logs = logs.withColumn('n', functions.lit(1))
    logs = logs.withColumn("xi^2", logs['xi'] * logs['xi'])
    logs = logs.withColumn("yi^2", logs['yi'] * logs['yi'])
    logs = logs.withColumn("xiyi", logs['xi'] * logs['yi'])
    sum_xi, sum_yi, n, sum_xi2, sum_yi2, sum_xiyi = logs\
        .groupBy()\
        .sum()\
        .cache()\
        .first()

    num = (n * sum_xiyi) - (sum_xi * sum_yi)
    den = math.sqrt((n * sum_xi2) - (sum_xi**2))\
        * math.sqrt((n * sum_yi2) - (sum_yi**2))

    r = num/den
    print("r = %g\nr^2 = %g" % (r, r**2))


if __name__ == '__main__':
    in_directory = sys.argv[1]
    main(in_directory)
