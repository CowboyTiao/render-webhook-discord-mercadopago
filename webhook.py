from flask import Flask, request, jsonify
import mercadopago
import json
import os
import pymysql
import requests

app = Flask(__name__)
sdk = mercadopago.SDK("APP_USR-8739880550401490-062716-ce4741df8269258e6066355f9156772f-1972922133")
DADOS_PAGAMENTO_PATH = "pagamentos.json"

# CONFIGURAÇÃO DO BANCO
DB_CONFIG = {
    "host": "localhost",
    "user": "discordbot",
    "password": "senha123",
    "database": "bewitched"         
}

def carregar_dados():
    if not os.path.exists(DADOS_PAGAMENTO_PATH):
        return {}
    with open(DADOS_PAGAMENTO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(DADOS_PAGAMENTO_PATH, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2)

def adicionar_coins(account_id, valor):
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("UPDATE characters SET coins = coins + %s WHERE id = %s", (valor, account_id))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[DB] Coins adicionados com sucesso para account_id {account_id}")
        return True
    except Exception as e:
        print(f"[ERRO DB] {e}")
        return False

# ✅ Adicionado para confirmar status da aplicação online
@app.route("/", methods=["GET"])
def root():
    return "Servidor do Webhook Mercado Pago online!", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "Webhook online!", 200

    payload = request.json
    print(f"[WEBHOOK] Payload recebido: {payload}")

    if not payload or "id" not in payload.get("data", {}):
        return jsonify({"status": "ignored"}), 200

    payment_id = payload["data"]["id"]
    result = sdk.payment().get(payment_id)
    data = result["response"]

    if data.get("status") == "approved":
        todos = carregar_dados()
        pagamento = todos.get(str(payment_id))

        if pagamento:
            account_id = pagamento["account_id"]
            valor = pagamento["valor"]
            nome = pagamento["nome"]

            print(f"[WEBHOOK] Pagamento aprovado! ID: {payment_id} | Usuário: {nome} | Valor: R${valor} | ID Discord: {account_id}")

            if adicionar_coins(account_id, int(valor)):
                try:
                    response = requests.post("http://localhost:5001/confirmar_pagamento", json={
                        "discord_id": account_id,
                        "valor": valor,
                        "nome": nome
                    })

                    if response.status_code == 200:
                        print(f"[WEBHOOK] ✅ Coins entregues e log enviado para {account_id}")
                    else:
                        print(f"[WEBHOOK] ⚠️ Falha ao enviar log: {response.status_code} - {response.text}")

                except Exception as e:
                    print(f"[WEBHOOK] ❌ ERRO ao enviar log para o bot: {e}")

                del todos[str(payment_id)]
                salvar_dados(todos)
            else:
                print(f"[WEBHOOK] ❌ Erro ao adicionar coins para {account_id}")
        else:
            print(f"[WEBHOOK] ⚠️ Pagamento {payment_id} não encontrado no JSON")

    return jsonify({"status": "received"}), 200

@app.route("/", methods=["POST"])
def webhook_fallback():
    payment_id = request.args.get("id")
    topic = request.args.get("topic")

    if topic == "payment" and payment_id:
        print(f"[WEBHOOK] Notificação recebida via fallback. ID: {payment_id}")

        # Consulta do pagamento usando SDK
        result = sdk.payment().get(payment_id)
        data = result["response"]

        if data.get("status") == "approved":
            todos = carregar_dados()
            pagamento = todos.get(str(payment_id))

            if pagamento:
                account_id = pagamento["account_id"]
                valor = pagamento["valor"]
                nome = pagamento["nome"]

                print(f"[WEBHOOK] Pagamento aprovado! ID: {payment_id} | Usuário: {nome} | Valor: R${valor} | ID Discord: {account_id}")

                if adicionar_coins(account_id, int(valor)):
                    try:
                        response = requests.post("http://localhost:5001/confirmar_pagamento", json={
                            "discord_id": account_id,
                            "valor": valor,
                            "nome": nome
                        })

                        if response.status_code == 200:
                            print(f"[WEBHOOK] ✅ Coins entregues e log enviado para {account_id}")
                        else:
                            print(f"[WEBHOOK] ⚠️ Falha ao enviar log: {response.status_code} - {response.text}")

                    except Exception as e:
                        print(f"[WEBHOOK] ❌ ERRO ao enviar log para o bot: {e}")

                    del todos[str(payment_id)]
                    salvar_dados(todos)
                else:
                    print(f"[WEBHOOK] ❌ Erro ao adicionar coins para {account_id}")
            else:
                print(f"[WEBHOOK] ⚠️ Pagamento {payment_id} não encontrado no JSON")

    return jsonify({"status": "received"}), 200

# ✅ Ajustado para funcionar no Render pegando a porta correta via variável de ambiente
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Webhook do Mercado Pago está online com sucesso na porta {port}!")
    app.run(host="0.0.0.0", port=port)
