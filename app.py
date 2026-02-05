from flask import Flask, make_response

app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
    return make_response("<h1> Hello World </h1>", 200)

if __name__ == "__main__":
    app.run(debug=True)