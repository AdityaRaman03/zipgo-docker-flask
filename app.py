from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "ZipGo service online for CIE set 95"

if __name__ == "__main__":
    # Bind to 0.0.0.0 and port 12096 so Docker can expose it
    app.run(host="0.0.0.0", port=12096)
