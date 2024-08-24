from flask import Flask, jsonify, request
from flask_cors import CORS
from nlp_models.llm_model import LaBSEModel
from nlp_models.tokenizer_model import WhitespaceTokenizer

app = Flask(__name__)
CORS(app)


@app.route("/encode", methods=["POST"])
def encode():
    data = request.json

    if "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    texts = data["text"]

    LaBSE = LaBSEModel()
    embd = LaBSE.encoding(texts)
    return jsonify({"embeddings": embd})


@app.route("/tokenize", methods=["POST"])
def tokenize():
    data = request.json
    text = data.get("text", "")

    tokenizer = WhitespaceTokenizer()
    words = tokenizer.tokenize(text)
    return jsonify({"tokens": words})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002)
