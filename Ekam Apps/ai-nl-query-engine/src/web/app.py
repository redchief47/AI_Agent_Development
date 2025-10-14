from flask import Flask

app = Flask(__name__)

# Middleware configuration can be added here

if __name__ == "__main__":
    app.run(debug=True)