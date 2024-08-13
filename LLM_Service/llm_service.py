from flask_cors import CORS
from flask import Flask, jsonify, request
from nlp_models.llm_model import LaBSEModel

app = Flask(__name__)
CORS(app)


@app.route("/encode", methods=["POST"])
def encode():
    data = request.json

    if "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    texts = data["text"]

    for text in data["text"]:
        if text is None:
            texts = ['Hi']
            break

    LaBSE = LaBSEModel()
    embd = LaBSE.encoding(texts)
    return jsonify({"embeddings": embd.tolist()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002)
