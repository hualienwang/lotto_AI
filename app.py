from flask import Flask, g
from src.routes import api_bp

app = Flask(__name__)
app.register_blueprint(api_bp)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    # Run locally on localhost only
    app.run(host='127.0.0.1', port=5000, debug=True)
