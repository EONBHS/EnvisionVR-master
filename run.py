from flask import Flask
from app import app

if __name__ == "__main__":
    app.secret_key = "abacadaba"
    app.run(debug=True)
