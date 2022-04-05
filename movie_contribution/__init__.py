import os
from flask import Flask, render_template

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Add some defaults which can be overridden later
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'title_contribution.sqlite'),
    )

    if test_config is not None:
        app.config.from_mapping(test_config)
    else:
        app.config.from_pyfile('config.py', silent=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import database
    database.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    @app.route('/health')
    def health_check():
        return 'Healthy!'

    @app.route('/')
    def index():
        return render_template('index.html')

    return app
