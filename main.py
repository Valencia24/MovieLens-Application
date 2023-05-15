#
# File: main.py
#
# Daniel Valencia
# MovieLens Application
# 
# This file represents the presentation tier of the program. It calls functions
# defined in the object tier to retrieve sql queries based on user input. There
# is functionality to lookup specific movies and details about them, retrieving
# the top N movies with a specified rating, and the ability to insert reviews as
# well as updating movie taglines. 
#

import sqlite3
import objecttier


# retrieve_movies:
#
# Prints out the total number of movies returned by a call to
# num_movies from the objecttier or an error message if none were found.
def retrieve_movies(dbConn):
    movies = objecttier.num_movies(dbConn)
    print("General stats:")

    # Error checking if movie count is not found
    if movies == -1:
        print("**No movies found...")
    else:
        print(" # of movies:", f"{movies:,}")


# retrieve_reviews:
#
# Prints out the total number of reviews returned by a call to
# num_reviews from the objecttier or an error message if none were found.
def retrieve_reviews(dbConn):
    reviews = objecttier.num_reviews(dbConn)

    # Error checking if review count is not found
    if reviews == -1:
        print("**No reviews found...")
    else:
        print(" # of reviews:", f"{reviews:,}")

# command_one:
#
# Prompts the user for a movie name pattern. Prints the number of
# movies found matching the input along with the movie id, name,
# and release year. If more than 100 movies were found, user is
# asked to narrow their search. If no movies were found, nothing is
# printed and the command loop continues.
def command_one(dbConn):
    print()
    prompt = "Enter movie name (wildcards _ and % supported): "
    name = input(prompt)

    movies = objecttier.get_movies(dbConn, name)

    # Error checking if 0 or 100+ movies were found
    if movies is None:
        return
    elif len(movies) > 100:
        print()
        print("# of movies found:", len(movies))
        print()
        print("There are too many movies to display, please narrow your search and try again...")
        return
    else:
        print()
        print("# of movies found:", len(movies))

        # Error checking if no movies found
        if len(movies) == 0:
            return
        print()

        for m in movies:
            print(m.Movie_ID, ":", m.Title, "({})".format(m.Release_Year))


# command_two:
#
# Prompts the user for a movie id. If the id is found, details about the movie are printed.
# If not, an error message will be printed instead.
def command_two(dbConn):
    print()
    prompt = "Enter movie id: "
    id = input(prompt)

    m = objecttier.get_movie_details(dbConn, id)

    # Check if movie id was not found
    if m is None:
        print()
        print("No such movie...")
        return
    else:
        print()
        print(m.Movie_ID, ":", m.Title)
        print(" Release date:", m.Release_Date)
        print(" Runtime:", m.Runtime, "(mins)")
        print(" Orig language:", m.Original_Language)
        print(" Budget:", f"${m.Budget:,}", "(USD)")
        print(" Revenue:", f"${m.Revenue:,}", "(USD)")
        print(" Num reviews:", m.Num_Reviews)
        print(" Avg rating:", "{:.2f}".format(m.Avg_Rating), "(0..10)")
        print(" Genres:", end=" ")

        for g in m.Genres:
            print(g, end=", ")
        print()
        print(" Production Companies:", end=" ")

        for c in m.Production_Companies:
            print(c, end=", ")
        print()
        print(" Tagline:", m.Tagline)


# command_three:
#
# Prompts the user for a number of movies and a minimum number of reviews. The number of
# movies/reviews should be positive (i.e greater than 0). If nothing is retrieved, there
# is nothing printed.
def command_three(dbConn):
    print()
    prompt_one = "N? "
    num_movies = input(prompt_one)

    # Check for negative input
    if int(num_movies) < 1:
        print("Please enter a positive value for N...")
        return

    prompt_two = "min number of reviews? "
    # Check for negative input
    num_revs = input(prompt_two)
    if int(num_revs) < 1:
        print("Please enter a positive value for min number of reviews...")
        return

    movies = objecttier.get_top_N_movies(dbConn, int(num_movies), int(num_revs))

    # Check if no movies/data was found
    if movies is None or movies == []:
        return

    print()
    for m in movies:
        print(m.Movie_ID, ":", m.Title, "({}),".format(m.Release_Year), "avg rating = ",
              "{:.2f}".format(m.Avg_Rating), "({} reviews)".format(m.Num_Reviews))


# command_four:
#
# Prompts the user for a rating between 0 - 10 and a movie id. If both inputs are valid,
# then a successful insertion message is printed. If not, the appropriate error message is
# printed instead.
def command_four(dbConn):
    print()
    prompt_one = "Enter rating (0..10): "
    rating = input(prompt_one)

    # Check if rating is valid
    if (int(rating) < 0 or int(rating) > 10):
        print("Invalid rating...")
        return

    prompt_two = "Enter movie id: "
    id = input(prompt_two)
    action = objecttier.add_review(dbConn, id, int(rating))

    # Check if the movie was not found
    if action == 0:
        print()
        print("No such movie...")
    else:
        print()
        print("Review successfully inserted")


##################################################################
#
# command_five:
#
# Prompts the user for a tagline and a movie id. If the id is not found, an error message
# is printed. If it is, then a successful message is printed instead.
#
def command_five(dbConn):
    print()
    prompt_one = "tagline? "
    tagline = input(prompt_one)

    prompt_two = "movie id? "
    id = input(prompt_two)

    action = objecttier.set_tagline(dbConn, id, tagline)
    # Check if no movie was found
    if action == 0:
        print()
        print("No such movie...")
    else:
        print()
        print("Tagline successfully set")


##################################################################
#
# main:
#

print("** Welcome to the MovieLens app **")
print()

dbConn = sqlite3.connect('MovieLens.db')
retrieve_movies(dbConn)
retrieve_reviews(dbConn)
print()

# Prompts user for commands, 'x' ends the program
command = input("Please enter a command (1-5, x to exit): ")
while command != "x":
    if command == "1":
        command_one(dbConn)
    elif command == "2":
        command_two(dbConn)
    elif command == "3":
        command_three(dbConn)
    elif command == "4":
        command_four(dbConn)
    elif command == "5":
        command_five(dbConn)

    print()
    command = input("Please enter a command (1-5, x to exit): ")
