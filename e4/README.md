## Movie Title Entity Resolution

For this question, we will use some movie rating data derived from the MovieTweetings data set.

The first thing you're given (`movie_list.txt` in the ZIP file) is a list of movie titles, one per line, like this:

```
Bad Moms
Gone in Sixty Seconds
Raiders of the Lost Ark
```

The second file (`movie_ratings.csv`) contains users' rating of movies: title and rating pairs. Well… the title, except the users have misspelled the titles.

```
title,rating
Bad Mods,8
Gone on Sixty Seconds,6.5
Gone in Six Seconds,7
```

The task for this question is to determine the average rating for each movie, compensating for the bad spelling in the ratings file. We will assume that the movie list file contains the correct spellings.

There are also some completely-incorrect titles that have nothing to do with the movie list. Those should be ignored. e.g.
Uhhh some movie i watched,7

Your command line should take the movie title list, movie ratings CSV, and the output CSV filename, like this:
`python3 average_ratings.py movie_list.txt movie_ratings.csv output.csv`

It should produce a CSV file (`output.csv` in the example above) with 'title' as the first column, and (average) 'rating' rounded to two decimal places as the second. The output should be sorted by title and include only movies with ratings in the data set.

```
title,rating
Bad Moms,8.0
Gone in Sixty Seconds,6.75
```

---

## Cities: Temperatures and Density

This question will combine information about cities from Wikidata with a different subset of the Global Historical Climatology Network data.

The question I have is: is there any correlation between population density and temperature? I admit it's an artificial question, but one we can answer. In order to answer the question, we're going to need to get population density of cities matched up with weather stations.

The program for this part should be named temperature_correlation.py and take the station and city data files in the format provided on the command line. The last command line argument should be the filename for the plot you'll output (described below).
`python3 temperature_correlation.py stations.json.gz city_data.csv output.svg`

### The Data

The collection of weather stations is quite large: it is given as a line-by-line JSON file that is gzipped. That is a fairly common format in the big data world. You can read the gzipped data directly with Pandas and it will automatically decompress as needed: `stations = pd.read_json(stations_file, lines=True)`

The 'avg_tmax' column in the weather data is °C×10 (because that's what GHCN distributes): it needs to be divided by 10. The value is the average of TMAX values from that station for the year: the average daily-high temperature.

The city data is in a nice convenient CSV file. There are many cities that are missing either their area or population: we can't calculate density for those, so they can be removed. Population density is population divided by area.

The city area is given in m², which is hard to reason about: convert to km². There are a few cities with areas that I don't think are reasonable: exclude cities with area greater than 10000 km².

### Entity Resolution

Both data sets contain a latitude and longitude, but they don't refer to exactly the same locations. A city's “location” is some point near the centre of the city. That is very unlikely to be the exact location of a weather station, but there is probably one nearby.

Find the weather station that is closest to each city. We need it's 'avg_tmax' value. This takes an kind of calculation: the distance between every city and station pair must be calculated.
