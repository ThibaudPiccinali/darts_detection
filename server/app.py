from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)

def fetch_all_scores():
    connection = sqlite3.connect("darts.db")
    cursor = connection.cursor()
    scores = cursor.execute("SELECT nom, score FROM scores").fetchall()
    connection.close()
    return scores

@app.route("/")
def index():
    return render_template("main.html")

# Route pour obtenir la valeur actuelle de la base de données
@app.route("/get_all_scores")
def get_all_scores():
    scores = fetch_all_scores()
    return jsonify({"scores": scores})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


