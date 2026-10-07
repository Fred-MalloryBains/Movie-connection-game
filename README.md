# Movie-connection-game

<img width="2940" height="1588" alt="demo_two" src="https://github.com/user-attachments/assets/3e746d67-af07-4690-9ca6-6ebcb95d04e6" />

* Test your movie knowledge by traversing between two actors using shared cast members! 
Select your own actors to create a challenge or use the random actor button to use 
popular selections. 

<br>

* Each turn enter a new cast member of the previous person to get closer to the goal actor, 
when you think the two actors share a movie submit finish game!

<br>

* When you are finished you can compare your links to the ones of the computer to see if you 
did better or worse. 

<img width="2940" height="1588" alt="demo_one" src="https://github.com/user-attachments/assets/e4e25b5e-bc48-447d-b18c-936b36fe940a" />


## Technology stack

### Frontend
* **HTML5 & CSS3:** (`style_m.css`).
* **JavaScript (ES6 Modules):** Modular client-side architecture handling dynamic DOM manipulation, real-time input autocomplete, game state lifecycle, and graph rendering.
* **Canvas API / Graph Visualisation:** Custom node-and-edge connection rendering (`graph.js`) displaying traversal paths between actors and movies.

### Backend & API
* **Python 3:** Core backend runtime.
* **Flask:** Lightweight REST API framework managing movie/actor queries, cast verification, and shortest-path requests.
* **Flask-CORS:** Cross-Origin Resource Sharing handling for secure frontend-to-backend communication across origins.
* **Flask-Admin & Flask-Migrate:** Administrative database management interface and Alembic-driven schema migrations.

### Database & Algorithms
* **SQLite / SQLAlchemy ORM:** Relational database modelling `Actor`, `Movie`, and `Cast` relationships with indexed lookups.
* **Graph Traversal (BFS):** Custom Breadth-First Search shortest-path algorithm (`min_links.py`) calculating optimal link degrees between actors.
* **TMDb (The Movie Database) API:** Seed pipeline and actor metadata enrichment.

### Infrastructure & Deployment
* **GitHub Pages:** Static hosting for the client application: [Movie Connection Game Link](https://fred-mallorybains.github.io/Movie-connection-game/)
* **GitHub Actions:** CI/CD deployment pipeline automating static build releases on push.
* **Cloudflare Tunnels (`cloudflared`):** Secure encrypted reverse proxy exposing the locally hosted Flask backend to the public web via a custom domain without opening incoming router ports.

## Highlights

* `seed.py` : custom seeding script using the tmdb api to find popular actors from top ranked movies, expandable and handles database relationships. <br>
* `min_links.py`: structured independent application using a two way graph search that handles incomplete db and API calls to find connections in O(n^2) instead of O(n^n). <br>
* `routes.py`: REST API management of features that handles backend requests for the game.

## NB 
Unfortunately the backend is no longer active 
