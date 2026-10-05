import os
import requests
from collections import deque
from dotenv import load_dotenv

load_dotenv()  # must run before os.environ is read

from app import db
from models import Actor, Movie

TMDB_API_KEY = os.environ["TMDB_API_KEY"]
TMDB_BASE_URL = os.environ.get("BASE_URL", "https://api.themoviedb.org/3")

MAX_BILLED = 8          # an actor "counts" in a movie only if billed in the top 8
MAX_MOVIES_PER_ACTOR = 15
session = requests.Session()


class ActorNotFound(Exception): ...
class TMDBError(Exception): ...


def tmdb_get(path):
    try:
        r = session.get(f"{TMDB_BASE_URL}{path}",
                        params={"api_key": TMDB_API_KEY}, timeout=5)
    except requests.RequestException as e:
        raise TMDBError(str(e)) from e
    if r.status_code == 404:
        return None
    if not r.ok:                      # 401 bad key, 429 rate limit, 5xx ...
        raise TMDBError(f"TMDB {r.status_code} on {path}")
    return r.json()


class Graph:
    """DB first (only if fully synced), TMDB fallback, memoised per search."""

    def __init__(self):
        self._actor_movies = {}
        self._movie_cast = {}

    # ---- actor -> movies ----
    def movies_of(self, actor_id):
        if actor_id not in self._actor_movies:
            actor = db.session.get(Actor, actor_id)

            if actor:
                ids = [cast_link.movie_id for cast_link in actor.movies]
            else:
                ids = []

            self._actor_movies[actor_id] = ids or self._fetch_actor_movies(actor_id)

        return self._actor_movies[actor_id]

    def _fetch_actor_movies(self, actor_id):
        data = tmdb_get(f"/person/{actor_id}/movie_credits")

        if data is None:
            return []

        cast = [
            movie for movie in data.get("cast", [])
            if movie.get("order", 99) < MAX_BILLED
        ]

        cast.sort(
            key=lambda movie: movie.get("popularity", 0),
            reverse=True
        )

        return [
            movie["id"]
            for movie in cast[:MAX_MOVIES_PER_ACTOR]
        ]

    # ---- movie -> actors ----
    def cast_of(self, movie_id):
        if movie_id not in self._movie_cast:
            movie = db.session.get(Movie, movie_id)

            if movie:
                ids = [cast_link.actor_id for cast_link in movie.cast]
            else:
                ids = []

            self._movie_cast[movie_id] = ids or self._fetch_movie_cast(movie_id)

        return self._movie_cast[movie_id]

    def _fetch_movie_cast(self, movie_id):
        data = tmdb_get(f"/movie/{movie_id}/credits")

        if data is None:
            return []

        cast = [
            actor for actor in data.get("cast", [])
            if actor.get("order", 99) < MAX_BILLED
        ]

        cast.sort(
            key=lambda actor: actor.get("popularity", 0),
            reverse=True
        )

        return [actor["id"] for actor in cast]


class Side:
    """One direction of the bidirectional BFS."""

    def __init__(self, root):
        self.parent = {root: None}       # actor -> (previous_actor, movie)
        self.dist = {root: 0}            # actor -> number of movies from root
        self.frontier = [root]
        self.depth = 0
        self.seen_movies = set()         # expand each movie once per direction

    def expand(self, graph, other):
        """Expand one full level. Returns the best meeting point found, if any."""
        best, nxt = None, []
        for actor in self.frontier:
            for movie in graph.movies_of(actor):
                if movie in self.seen_movies:
                    continue
                self.seen_movies.add(movie)
                for costar in graph.cast_of(movie):
                    if costar == actor:
                        continue
                    if costar in other.parent:
                        total = self.depth + 1 + other.dist[costar]
                        if best is None or total < best[0]:
                            best = (total, actor, movie, costar)
                    if costar not in self.parent:
                        self.parent[costar] = (actor, movie)
                        self.dist[costar] = self.depth + 1
                        nxt.append(costar)
        self.frontier, self.depth = nxt, self.depth + 1
        return best


def _walk(parent, node):
    """[node, movie, actor, ..., root]"""
    out = [{"type": "actor", "id": node}]
    while parent[node] is not None:
        node, movie = parent[node]
        out += [{"type": "movie", "id": movie}, {"type": "actor", "id": node}]
    return out


def find_path(start_id, target_id, max_movies=6):
    if start_id == target_id:
        return {"connections": 0, "path": [{"type": "actor", "id": start_id}]}

    graph = Graph()
    for actor_id in (start_id, target_id):
        if not graph.movies_of(actor_id):
            raise ActorNotFound(f"No TMDB credits for actor {actor_id}")

    fwd, bwd = Side(start_id), Side(target_id)
    while fwd.frontier and bwd.frontier and fwd.depth + bwd.depth < max_movies:
        side, other = (fwd, bwd) if len(fwd.frontier) <= len(bwd.frontier) else (bwd, fwd)
        hit = side.expand(graph, other)
        if hit:
            total, actor, movie, costar = hit
            a_f, a_b = (actor, costar) if side is fwd else (costar, actor)
            path = (list(reversed(_walk(fwd.parent, a_f)))
                    + [{"type": "movie", "id": movie}]
                    + _walk(bwd.parent, a_b))
            return {"connections": total, "path": path}
    return None