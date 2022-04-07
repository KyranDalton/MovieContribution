# Movie Contribution

### Overview
A prototype webapp to add, update and delete movies to the movie database.

### User Guide

#### Sign up
Sign-ups require a username, email and password. Click register in the navigation bar or go to /auth/register to create an account.

#### Login
To login to your account, click the login button in the navigation bar or go to /auth/login.

#### Logout
Press the logout button in the navigation bar, you will be ask to confirm before logging out.

#### View existing movies
You can view existing movies on the home page (/) when logged in.

#### Add a new movie
You can add a new movie by clicking `New Movie` on the home page (/) or by going to /add.

Here you will be asked for a movie title and movie plot.

#### Update an existing movie
You can update the details (title and plot) for an existing movie by clicking `Edit` for that movie on the home page (/).

#### Delete a movie
Only admin users can delete a movie. To delete a movie go to the update page (see above) for the movie and click `Delete`, you will be asked to confirm this.

### Bootstrap

1. Pull this package locally, either by downloading or using git.
2. Navigate to the package locally and create a new virtual environment `python3 -m venv venv`
3. Shell into the virtual environment `. env/bin/activate`
4. Install the dependencies `pip install -r requirements.txt`
5. Export required variables `export FLASK_APP=movie_contribution` & `export FLASK_ENV=development`
6. Initialize the SQLite DB `flask init-db`
7. Run the development server `flask run`
8. Go to http://127.0.0.1:5000/ to see the running app

### Development

Useful commands:
- `flask run` - runs the application
- `python -m pytest` - runs the unit tests
- `coverage run -m pytest` - to collect the test coverage
- `coverage report -m --omit="*/tst*"` - to view the test coverage
  