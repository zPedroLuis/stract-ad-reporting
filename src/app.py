from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    print("Acessando a raiz da API...")
    return jsonify({
        "name": "Pedro Luis Pereira Morais",
        "email": "zpedroluis@outlook.com",
        "linkedin": "https://www.linkedin.com/in/zPedroLuis"
    })

if __name__ == '__main__':
    app.run(debug=True)
