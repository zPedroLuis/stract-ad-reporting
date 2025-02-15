from flask import Flask, Response
import csv
import io
import urllib.request
import json
app = Flask(__name__)

BASE_URL = "https://sidebar.stract.to/api/insights"
def fetch_json(url, headers):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            if response.getcode() == 200:
                data = response.read().decode("utf-8")
                return json.loads(data)
            else:
                raise Exception(f"Erro na requisição: {response.getcode()} - {response.read().decode('utf-8')}")
    except urllib.error.URLError as e:
        raise Exception(f"Erro de conexão: {e.reason}")

def get_all_platforms():
    url = "https://sidebar.stract.to/api/platforms"
    headers = {
        "Authorization": "Bearer ProcessoSeletivoStract2025"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            if response.getcode() == 200:
                data = response.read().decode("utf-8")
                platforms_data = json.loads(data)
                platforms = [platform["value"] for platform in platforms_data.get("platforms", [])]
                return platforms
            else:
                return []
    except urllib.error.URLError as e:
        return []
def get_all_fields(platform):
    url = f"https://sidebar.stract.to/api/fields?platform={platform}"
    fields = []
    current_page = 1
    try:
        while True:
            data = fetch_json(f"{url}&page={current_page}", {"Authorization": "Bearer ProcessoSeletivoStract2025"})
            if "fields" not in data:
                return []  # Retorna uma lista vazia em caso de erro
            fields.extend(data["fields"])
            if "pagination" in data:
                total_pages = data["pagination"]["total"]
                if current_page >= total_pages:
                    break
                current_page += 1
            else:
                break
    except Exception as e:
        return []  # Retorna uma lista vazia em caso de erro
    
    return [field["value"] for field in fields]
def get_all_accounts(platform):
    url = f"https://sidebar.stract.to/api/accounts?platform={platform}"
    accounts = []
    current_page = 1
    try:
        while True:
            data = fetch_json(f"{url}&page={current_page}", {"Authorization": "Bearer ProcessoSeletivoStract2025"})
            if "accounts" not in data:
                return []  # Retorna uma lista vazia em caso de erro
            accounts.extend(data["accounts"])
            if "pagination" in data:
                total_pages = data["pagination"]["total"]
                if current_page >= total_pages:
                    break
                current_page += 1
            else:
                break
    except Exception as e:
        return []  # Retorna uma lista vazia em caso de erro
    
    return accounts
def get_insights(platform, account, fields):
    if "ad_name" not in fields:
        fields.append("ad_name")
    fields_str = ",".join(fields)
    url = f"{BASE_URL}?platform={platform}&account={account['id']}&token={account['token']}&fields={fields_str}"
    response = fetch_json(url, {"Authorization": "Bearer ProcessoSeletivoStract2025"})
    if "insights" not in response or not response["insights"]:
        return []
    return response["insights"]
def generate_csv(data, fields):
    output = io.StringIO()
    ordered_fields = ["Platform", "Account Name"] + [field for field in fields if field not in ["Platform", "Account Name"]]
    writer = csv.DictWriter(output, fieldnames=ordered_fields, delimiter=",", lineterminator="\n")
    writer.writeheader()
    for row in data:
        full_row = {field: row.get(field, "") for field in ordered_fields}
        writer.writerow(full_row)
    return output.getvalue()
@app.route("/", methods=["GET"])
def root():
    data = {
        "name": "Pedro Luis Pereira Morais",
        "email": "zpedroluis@outlook.com",
        "linkedin": "https://www.linkedin.com/in/zPedroLuis"
    }
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data.keys())
    writer.writeheader()
    writer.writerow(data)
    csv_data = output.getvalue()
    csv_data_with_bom = "\ufeff" + csv_data
    return Response(
        csv_data_with_bom,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=home.csv"}
    )
@app.route("/<platform>", methods=["GET"])
def platform_data(platform):
    fields = get_all_fields(platform)
    accounts = get_all_accounts(platform)
    data = []
    for account in accounts:
        insights = get_insights(platform, account, fields)
        for insight in insights:
            row = {
                "Platform": platform,
                "Account Name": account["name"],
                "ad_name": insight.get("ad_name", ""),
            }
            for field in fields:
                value = insight.get(field, "")
                if field in ["clicks", "impressions", "spend", "cpc", "ctr", "ctr_unique"]:
                    try:
                        if isinstance(value, str):
                            value = float(value)
                        elif not isinstance(value, (int, float)):
                            value = ""
                    except ValueError:
                        value = ""
                row[field] = value
            data.append(row)
    csv_data = generate_csv(data, fields)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={platform}_report.csv"}
    )

@app.route("/<platform>/resumo", methods=["GET"])
def platform_summary(platform):
    fields = get_all_fields(platform)
    accounts = get_all_accounts(platform)
    numeric_fields = ["clicks", "impressions", "spend", "cpc", "ctr", "ctr_unique"]
    summary_data = {}
    for account in accounts:
        insights = get_insights(platform, account, fields)
        account_name = account["name"]
        
        if account_name not in summary_data:
            summary_data[account_name] = {
                "Platform": platform,
                "Account Name": account_name,
                "Ad Name": "",  # Deixar vazio
            }
            for field in numeric_fields:
                summary_data[account_name][field] = 0.0  # Usar float em vez de int
        for insight in insights:
            for field in numeric_fields:
                value = insight.get(field, 0.0)  # Valor padrão como float
                try:
                    if isinstance(value, str):  # Se for string, converter para float
                        value = float(value)
                    elif not isinstance(value, (int, float)):  # Se não for número, ignorar
                        value = 0.0
                    summary_data[account_name][field] += value
                except ValueError:
                    continue
    data = list(summary_data.values())
    formatted_data = []
    for row in data:
        formatted_row = row.copy()
        for field in numeric_fields:
            if field == "clicks" or field == "impressions":
                formatted_row[field] = int(round(row[field], 0))
            else:
                formatted_row[field] = round(row[field], 3)
        formatted_data.append(formatted_row)
    csv_data = generate_csv(formatted_data, numeric_fields)  # Corrigido aqui
    csv_data_with_bom = "\ufeff" + csv_data
    return Response(
        csv_data_with_bom,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={platform}_summary.csv"
        }
    )

@app.route("/geral", methods=["GET"])
def general_report():
    platforms = get_all_platforms()
    all_data = []
    for platform in platforms:
        fields = get_all_fields(platform)
        accounts = get_all_accounts(platform)
        if not accounts:
            continue
        for account in accounts:
            insights = get_insights(platform, account, fields)
            if not insights:
                continue
            for insight in insights:
                row = {
                    "Platform": platform,
                    "Account Name": account["name"],
                }
                for field in fields:
                    value = insight.get(field, "")
                    if field in ["clicks", "impressions", "spend", "cpc", "ctr", "ctr_unique"]:
                        try:
                            if isinstance(value, str):
                                value = float(value)
                            elif not isinstance(value, (int, float)):
                                value = ""
                        except ValueError:
                            value = ""
                    row[field] = value
                all_data.append(row)
    all_fields = set()
    for row in all_data:
        all_fields.update(row.keys())
    ordered_fields = ["Platform", "Account Name"] + sorted([field for field in all_fields if field not in ["Platform", "Account Name"]])
    csv_data = generate_csv(all_data, ordered_fields)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=general_report.csv"}
    )

@app.route("/geral/resumo", methods=["GET"])
def general_summary():
    platforms = get_all_platforms()
    summary_data = {}
    for platform in platforms:
        fields = get_all_fields(platform)
        accounts = get_all_accounts(platform)
        numeric_fields = ["clicks", "impressions", "spend", "cpc", "ctr", "ctr_unique"]
        if platform not in summary_data:
            summary_data[platform] = {
                "Platform": platform,
            }
            for field in numeric_fields:
                summary_data[platform][field] = 0.0
        for account in accounts:
            insights = get_insights(platform, account, fields)
            for insight in insights:
                for field in numeric_fields:
                    value = insight.get(field, 0.0)  # Valor padrão como float
                    try:
                        if isinstance(value, str):  # Se for string, converter para float
                            value = float(value)
                        elif not isinstance(value, (int, float)):  # Se não for número, ignorar
                            value = 0.0
                        summary_data[platform][field] += value
                    except ValueError:
                        continue
    data = list(summary_data.values())
    formatted_data = []
    for row in data:
        formatted_row = row.copy()
        for field in numeric_fields:
            if field == "clicks" or field == "impressions":
                formatted_row[field] = int(round(row[field], 0))
            else:
                formatted_row[field] = round(row[field], 3)
        formatted_data.append(formatted_row)
    all_fields = ["Platform"] + numeric_fields
    csv_data = generate_csv(formatted_data, all_fields)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=general_summary.csv"
        }
    )

if __name__ == "__main__":
    app.run(debug=True)