from flask import Flask, request, jsonify

app = Flask(__name__)

bin_data = {
    "distance": 0,
    "fill": 0
}

@app.route("/update", methods=["POST"])
def update():
    global bin_data
    data = request.json
    bin_data["distance"] = data["distance"]
    bin_data["fill"] = data["fill"]
    return jsonify({"status": "success"})

@app.route("/data", methods=["GET"])
def data():
    return jsonify(bin_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)