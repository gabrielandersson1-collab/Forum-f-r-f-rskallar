from flask import Flask
from forum.routes import main

app = Flask(__name__)
app.secret_key = "byt-ut-mig-till-nagot-eget"

# Kopplar in alla sidor från routes.py
app.register_blueprint(main)

if __name__ == "__main__":
    app.run(debug=True)