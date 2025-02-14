from flask import Flask, jsonify, request
import urllib.request
import json

app = Flask(__name__)

BASE_URL = "https://sidebar.stract.to/api/"

def get_api_data(endpoint=""):
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": "Bearer ProcessoSeletivoStract2025"
    }

    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request) as response:
            response_data = response.read()
            text_data = response_data.decode('utf-8').strip()

            if text_data.startswith('{') or text_data.startswith('['):
                try:
                    data = json.loads(text_data)
                except json.JSONDecoderError as e:
                    data = {"error": f"Erro ao decodificar JSON: {e}", "raw": text_data}
            else:
                data = {"raw": text_data}    
                
    except Exception as e:
        print("Erro na requisição: ", e)
        data = {"error": str(e)}

    return data

@app.route('/')
def home():
    return jsonify({
        "name": "Pedro Luis Pereira Morais",
        "email": "zpedroluis@outlook.com",
        "linkedin": "https://www.linkedin.com/in/zPedroLuis"
    })

@app.route('/api/data')
def api_data():
    data = get_api_data()
    return jsonify(data)

@app.route('/api/platforms', methods = ['GET'])
def get_platforms():
    data = get_api_data("platforms")
    return jsonify(data.get('platforms',[]))

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    platform = request.args.get('platform', '')

    if not platform:
        return jsonify({"error": "O parâmetro 'platform' é obrigatório"}), 400
    
    data = get_api_data(f"accounts?platform={platform}")    
    return  jsonify(data.get('accounts', []))

@app.route('/api/fields', methods = ['GET'])
def get_fields():
    platform = request.args.get('platform', '')

    if not platform:
        return jsonify({"error": "O parâmetro 'platform' é obrigatório"}), 400
    
    data = get_api_data(f"fields?platform={platform}")
    return jsonify(data.get('fields', []))

@app.route('/api/insights', methods=['GET'])
def get_insights():
    platform = request.args.get('platform', '')
    account = request.args.get('account', '')
    token = request.args.get('token', '')
    fields = request.args.get('fields', '').split(',')

    if not platform or not account or not token or not fields:
        return jsonify({"error": "Os parâmetros 'platform', 'account', 'token' e 'fields' são obrigatórios."}), 400
    
    fields_str = ','.join(fields)
    endpoint = f"insights?platform={platform}&account={account}&token={token}&fields={fields_str}"

    data = get_api_data(endpoint)

    if 'error' in data:
        return jsonify(data), 500
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
