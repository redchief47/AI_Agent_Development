from flask import Flask
from web_interface.routes import setup_routes

def create_app():
    app = Flask(__name__)
    
    # Set up routes
    setup_routes(app)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)