#
# File: objecttier.py
#
# This file represents the Object tier and contains the sql queries that will
# be called in the datatier. There is functionality to retrieve the total
# number of movies and reviews, list of movies matching user input, all info
# about a movie, and a list of N movies with a certain average rating. There
# is also functionality for modifying the database with insertion and update
# actions.
#
# Daniel Valencia
# MovieLens Application
#

import datatier


class Movie:
    def __init__(self, id, title, year):
        self._Movie_ID = id
        self._Title = title
        self._Release_Year = year

    @property
    def Movie_ID(self):
        return self._Movie_ID

    @property
    def Title(self):
        return self._Title

    @property
    def Release_Year(self):
        return self._Release_Year


class MovieRating:
    def __init__(self, id, title, year, num_reviews, avg_rating):
        self._Movie_ID = id
        self._Title = title
        self._Release_Year = year
        self._Num_Reviews = num_reviews
        self._Avg_Rating = avg_rating

    @property
    def Movie_ID(self):
        return self._Movie_ID

    @property
    def Title(self):
        return self._Title

    @property
    def Release_Year(self):
        return self._Release_Year

    @property
    def Num_Reviews(self):
        return self._Num_Reviews

    @property
    def Avg_Rating(self):
        return self._Avg_Rating


class MovieDetails:
    def __init__(self, id, title, num_reviews, avg_rating,
                 release_date, runtime, language, budget,
                 revenue, tagline):
        self._Movie_ID = id
        self._Title = title
        self._Num_Reviews = num_reviews
        self._Avg_Rating = avg_rating
        self._Release_Date = release_date
        self._Runtime = runtime
        self._Original_Language = language
        self._Budget = budget
        self._Revenue = revenue
        self._Tagline = tagline
        self._Genres = []
        self._Production_Companies = []

    @property
    def Movie_ID(self):
        return self._Movie_ID

    @property
    def Title(self):
        return self._Title

    @property
    def Num_Reviews(self):
        return self._Num_Reviews

    @property
    def Avg_Rating(self):
        return self._Avg_Rating

    @property
    def Release_Date(self):
        return self._Release_Date

    @property
    def Runtime(self):
        return self._Runtime

    @property
    def Original_Language(self):
        return self._Original_Language

    @property
    def Budget(self):
        return self._Budget

    @property
    def Revenue(self):
        return self._Revenue

    @property
    def Tagline(self):
        return self._Tagline

    @property
    def Genres(self):
        return self._Genres

    @property
    def Production_Companies(self):
        return self._Production_Companies


# num_movies:
#
# Returns: # of movies in the database; if an error returns -1
def num_movies(dbConn):
    sql = "Select count(*) From Movies;"
    row = datatier.select_one_row(dbConn, sql)

    # Perform error checking for data retrieval
    if row is None:
        return -1

    movies = row[0]
    return movies


# num_reviews:
#
# Returns: # of reviews in the database; if an error returns -1
def num_reviews(dbConn):
    sql = "Select count(*) From Ratings;"
    row = datatier.select_one_row(dbConn, sql)

    # Perform error checking for data retrieval
    if row is None:
        return -1

    reviews = row[0]
    return reviews


# get_movies:
#
# gets and returns all movies whose name are "like"
# the pattern. Patterns are based on SQL, which allow
# the _ and % wildcards. Pass "%" to get all stations.
#
# Returns: list of movies in ascending order by name; 
#          an empty list means the query did not retrieve
#          any data (or an internal error occurred, in
#          which case an error msg is already output).
def get_movies(dbConn, pattern):
    sql = """Select Movie_ID, Title, strftime('%Y', Release_Date)
    From Movies Where Title like ? Order By Title asc;"""
    rows = datatier.select_n_rows(dbConn, sql, [pattern])

    # Perform error checking for data retrieval
    if rows is None:
        return None

    # Create a new Movie object using data from query and append it to list
    movies = []
    for row in rows:
        movies.append(Movie(row[0], row[1], row[2]))

    return movies


# get_movie_details:
#
# gets and returns details about the given movie; you pass
# the movie id, function returns a MovieDetails object. Returns
# None if no movie was found with this id.
#
# Returns: if the search was successful, a MovieDetails obj
#          is returned. If the search did not find a matching
#          movie, None is returned; note that None is also 
#          returned if an internal error occurred (in which
#          case an error msg is already output).
def get_movie_details(dbConn, movie_id):
    sql = """Select Movies.Movie_ID, Title, date(Release_Date),
    Runtime, Original_Language, Budget, Revenue From Movies
    Where Movies.Movie_ID = ?"""
    row = datatier.select_one_row(dbConn, sql, [movie_id])

    # Perform error checking in case the movie id was not found
    if row == ():
        return None

    # Store data values retrieved
    id = row[0]
    title = row[1]
    rel_date = row[2]
    runtime = row[3]
    lang = row[4]
    budget = row[5]
    revenue = row[6]

    # Query to retrieve rating info
    sql = """Select count(Rating), avg(Rating) From Ratings
    Where Ratings.Movie_ID = ? Group By Ratings.Movie_ID"""
    rating = datatier.select_one_row(dbConn, sql, [movie_id])

    # Store rating values or provide default values if rating info does not exist
    if rating == ():
        num_rev = 0
        avg_rat = 0.00
    else:
        num_rev = rating[0]
        avg_rat = rating[1]

    # Query to retrieve tagline info
    sql = """Select Tagline From Movie_Taglines Where
    Movie_Taglines.Movie_ID = ?"""
    tag = datatier.select_one_row(dbConn, sql, [movie_id])

    # Store tagline or provide default value if tagline info does not exist
    if tag == ():
        tagline = ""
    else:
        tagline = tag[0]

    # Create a new MovieDetails object using stored values
    movie = MovieDetails(id, title, num_rev, avg_rat,
                         rel_date, runtime, lang, budget, revenue, tagline)

    # Query to retrieve list of production companies for movie
    sql = """Select Movie_Production_Companies.Movie_ID,
    Company_Name From Movie_Production_Companies Inner Join
    Companies On Movie_Production_Companies.Company_ID =
    Companies.Company_ID Where
    Movie_Production_Companies.Movie_ID = ? Order By
    Company_Name Asc"""
    rows = datatier.select_n_rows(dbConn, sql, [movie_id])

    # Add list of companies to MovieDetails, default value provided if no companies
    for row in rows:
        name = row[1]
        if name is None:
            name = ""
            break

        movie._Production_Companies.append(name)

    # Query to retrieve list of genres for movie
    sql = """Select Movie_Genres.Movie_ID, Genre_Name From
    Movie_Genres Inner Join Genres on Movie_Genres.Genre_ID
    = Genres.Genre_ID Where Movie_Genres.Movie_ID = ?
    Order By Genre_Name Asc"""

    # Add list of genres to MovieDetails, default value provided if no genres
    g_rows = datatier.select_n_rows(dbConn, sql, [movie_id])
    for g in g_rows:
        genre = g[1]
        if genre is None:
            genre = ""
            break

        movie._Genres.append(genre)

    return movie


# get_top_N_movies:
#
# gets and returns the top N movies based on their average 
# rating, where each movie has at least the specified # of
# reviews. Example: pass (10, 100) to get the top 10 movies
# with at least 100 reviews.
#
# Returns: returns a list of 0 or more MovieRating objects;
#          the list could be empty if the min # of reviews
#          is too high. An empty list is also returned if
#          an internal error occurs (in which case an error 
#          msg is already output).
def get_top_N_movies(dbConn, N, min_num_reviews):
    sql = """Select Movies.Movie_ID, Title, strftime('%Y', Release_Date),
    avg(Rating), count(Rating) From Movies Inner Join Ratings On
    Movies.Movie_ID = Ratings.Movie_ID Group By Ratings.Movie_ID Having
    count(Rating) >= ? Order By avg(Rating) desc Limit ?"""
    rows = datatier.select_n_rows(dbConn, sql, [int(min_num_reviews), int(N)])

    # Error checking if no data is retrieved
    if rows is None:
        return None

    # Check for excessive amount of reviews
    movies = []
    if int(N) >= 1000:
        return movies

    # Create new MovieRating object and add it to list of movies
    for row in rows:
        movies.append(MovieRating(row[0], row[1], row[2], row[4], row[3]))

    return movies


# add_review:
#
# Inserts the given review --- a rating value 0..10 --- into
# the database for the given movie. It is considered an error
# if the movie does not exist (see below), and the review is
# not inserted.
#
# Returns: 1 if the review was successfully added, returns
#          0 if not (e.g. if the movie does not exist, or if
#          an internal error occurred).
def add_review(dbConn, movie_id, rating):
    sql = "Select Movies.Movie_ID from Movies Where Movies.Movie_ID = ?"
    row = datatier.select_one_row(dbConn, sql, [movie_id])

    # Check if the movie id does not exist
    if row == ():
        return 0

    # Query to modify database and insert a new rating for the movie
    sql = "Insert Into Ratings(Movie_ID, Rating) Values (?, ?)"
    action = datatier.perform_action(dbConn, sql, [movie_id, rating])

    # Check if the insertion was not successful
    if action == -1:
        return 0

    return 1


# set_tagline:
#
# Sets the tagline --- summary --- for the given movie. If
# the movie already has a tagline, it will be replaced by
# this new value. Passing a tagline of "" effectively 
# deletes the existing tagline. It is considered an error
# if the movie does not exist (see below), and the tagline
# is not set.
#
# Returns: 1 if the tagline was successfully set, returns
#          0 if not (e.g. if the movie does not exist, or if
#          an internal error occurred).
def set_tagline(dbConn, movie_id, tagline):
    sql = "Select Movies.Movie_ID From Movies Where Movies.Movie_ID = ?"
    row = datatier.select_one_row(dbConn, sql, [movie_id])

    # Check if the movie does not exist
    if row == ():
        return 0

    # Query that retrieves tagline
    sql = "Select Tagline From Movie_Taglines Where Movie_Taglines.Movie_ID = ?"
    tag = datatier.select_one_row(dbConn, sql, [movie_id])

    # Check if the tagline is empty
    if tag == ():
        sql = "Insert Into Movie_Taglines(Movie_ID, Tagline) Values(?, ?)"
        action = datatier.perform_action(dbConn, sql, [movie_id, tagline])

        # Check if insertion was not successful
        if action == -1:
            return 0
    else:
        # If tagline already exists, update to new tagline
        sql = """Update Movie_Taglines Set Tagline = ? Where Movie_Taglines.Movie_ID
        = ?"""
        action = datatier.perform_action(dbConn, sql, [tagline, movie_id])

        # Check if update was not successful
        if action == -1:
            return 0

    return 1
