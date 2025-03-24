import tmdbsimple as tmdb
import requests

from dotenv import load_dotenv

import os 

load_dotenv()

tmdb.API_KEY = os.getenv('API_KEY')
BASE_URL = "https://api.themoviedb.org/3"





def get_actor (actor_name):
    search = tmdb.Search()
    response = search.person(query= actor_name)
    actor = response['results'][0]
    return actor 

def get_movies (actor):
    # Get actor's movie credits
    person = tmdb.People(actor['id'])
    credits = person.movie_credits()
    
    # List movies
    char_movies = {}
    for movie in credits['cast']:
        char_movies[movie['title']] = []
        for name in tmdb.Movies(movie['id']).credits()['cast']:
            char_movies[movie['title']].append(name['name'])
    return char_movies

def search_movie (movies, actor_name):
    for movie in movies:
        if actor_name in movies[movie]:
            return movie
    return None

def end_game ():
    print ("you lost!! ")
    exit()

def Start_Game ():
    start_actor = input ("Enter Initial Actor Name: ")
    goal_actor = get_actor(input ("Enter Goal Actor Name: "))
    first_actor = get_actor(start_actor)
    next_actor = {'name': ''}
    while (next_actor['name'] != goal_actor['name']):
        movies = get_movies(first_actor)
        next_actor = get_actor(input("Enter next actor name: "))
        movie = search_movie(movies, next_actor['name'])
        if movie:
            print(f"{first_actor['name']} and {next_actor['name']} were in {movie}")
        else:
            print ("No link found")
            end_game()
        first_actor = next_actor
    print ("You won!!")
    exit()
    
if __name__ == "__main__":
    Start_Game()
    
    