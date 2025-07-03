from flask import Flask, request, jsonify
import mercadopago
import json
import os
import pymysql
import requests
import time  # necessário para o sleep

app = Flask(__name__)
sdk = mercadopago.SDK("APP_USR-8739880550401490-062716-ce4741df8269258e6066355f9156772f-1972922133")

# Caminho absoluto do JSON, garante que está na pasta do webhook
DADOS_PAGAMENTO_PATH = os.path.join(os.path.dirname(__file__), "pagamentos.json")

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

def adicionar_coins(character_id, valor):
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("UPDATE characters SET coins = coins + %s WHERE id = %s", (valor, character_id))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[DB] Coins adicionados com sucesso para character_id {character_id}")
        return True
    except Exception as e:
        print(f"[ERRO DB] {e}")
        return False

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
        time.sleep(5)  # ⏳ tempo de espera ANTES da tentativa de ler o JSON

        tentativas = 5
        pagamento = None

        for i in range(tentativas):
            todos = carregar_dados()
            pagamento = todos.get(str(payment_id))
            if pagamento:
                print(f"[WEBHOOK] ✅ Pagamento {payment_id} encontrado no JSON na tentativa {i+1}")
                break
            print(f"[WEBHOOK] ⚠️ Tentativa {i+1}/{tentativas}: Pagamento {payment_id} ainda não está no JSON...")
            time.sleep(1)

        if not pagamento:
            print(f"[WEBHOOK] ❌ Pagamento {payment_id} não localizado após {tentativas} tentativas.")
            return jsonify({"status": "ignored"}), 200

        character_id = pagamento["character_id"]
        valor = pagamento["valor"]
        nome = pagamento["nome"]

        print(f"[WEBHOOK] Pagamento aprovado! ID: {payment_id} | Usuário: {nome} | Valor: R${valor} | ID Personagem: {character_id}")

        if adicionar_coins(character_id, int(valor)):
            try:
                response = requests.post("http://localhost:5001/confirmar_pagamento", json={
                    "discord_id": character_id,
                    "valor": valor,
                    "nome": nome
                })

                if response.status_code == 200:
                    print(f"[WEBHOOK] ✅ Coins entregues e log enviado para {character_id}")
                else:
                    print(f"[WEBHOOK] ⚠️ Falha ao enviar log: {response.status_code} - {response.text}")

            except Exception as e:
                print(f"[WEBHOOK] ❌ ERRO ao enviar log para o bot: {e}")

            del todos[str(payment_id)]
            salvar_dados(todos)
        else:
            print(f"[WEBHOOK] ❌ Erro ao adicionar coins para {character_id}")

    return jsonify({"status": "received"}), 200

@app.route("/", methods=["POST"])
def webhook_fallback():
    payment_id = request.args.get("id")
    topic = request.args.get("topic")

    if topic == "payment" and payment_id:
        print(f"[WEBHOOK] Notificação recebida via fallback. ID: {payment_id}")
        result = sdk.payment().get(payment_id)
        data = result["response"]

        if data.get("status") == "approved":
            time.sleep(2)  # ⏳ tempo de espera ANTES da tentativa de ler o JSON

            tentativas = 3
            pagamento = None

            for i in range(tentativas):
                todos = carregar_dados()
                pagamento = todos.get(str(payment_id))
                if pagamento:
                    print(f"[WEBHOOK] ✅ Pagamento {payment_id} encontrado no JSON na tentativa {i+1}")
                    break
                print(f"[WEBHOOK] ⚠️ Tentativa {i+1}/{tentativas}: Pagamento {payment_id} ainda não está no JSON...")
                time.sleep(1)

            if not pagamento:
                print(f"[WEBHOOK] ❌ Pagamento {payment_id} não localizado após {tentativas} tentativas.")
                return jsonify({"status": "ignored"}), 200

            character_id = pagamento["character_id"]
            valor = pagamento["valor"]
            nome = pagamento["nome"]

            print(f"[WEBHOOK] Pagamento aprovado! ID: {payment_id} | Usuário: {nome} | Valor: R${valor} | ID Personagem: {character_id}")

            if adicionar_coins(character_id, int(valor)):
                try:
                    response = requests.post("http://localhost:5001/confirmar_pagamento", json={
                        "discord_id": character_id,
                        "valor": valor,
                        "nome": nome
                    })

                    if response.status_code == 200:
                        print(f"[WEBHOOK] ✅ Coins entregues e log enviado para {character_id}")
                    else:
                        print(f"[WEBHOOK] ⚠️ Falha ao enviar log: {response.status_code} - {response.text}")

                except Exception as e:
                    print(f"[WEBHOOK] ❌ ERRO ao enviar log para o bot: {e}")

                del todos[str(payment_id)]
                salvar_dados(todos)
            else:
                print(f"[WEBHOOK] ❌ Erro ao adicionar coins para {character_id}")

    return jsonify({"status": "received"}), 200
import threading

def verificador_pendencias():
    while True:
        print("[VERIFICADOR] Iniciando varredura de pagamentos pendentes...")
        dados = carregar_dados()

        if not dados:
            print("[VERIFICADOR] Nenhum pagamento pendente.")
        else:
            for payment_id, pagamento in list(dados.items()):
                try:
                    result = sdk.payment().get(payment_id)
                    data = result["response"]
                    status = data.get("status", "")

                    if status == "approved":
                        character_id = pagamento["character_id"]
                        valor = pagamento["valor"]
                        nome = pagamento["nome"]

                        print(f"[VERIFICADOR] ⚠️ Pagamento {payment_id} aprovado mas ainda não processado!")
                        if adicionar_coins(character_id, int(valor)):
                            try:
                                response = requests.post("http://localhost:5001/confirmar_pagamento", json={
                                    "discord_id": character_id,
                                    "valor": valor,
                                    "nome": nome
                                })
                                if response.status_code == 200:
                                    print(f"[VERIFICADOR] ✅ Coins entregues e log enviado para {character_id}")
                                else:
                                    print(f"[VERIFICADOR] ⚠️ Falha ao enviar log: {response.status_code} - {response.text}")
                            except Exception as e:
                                print(f"[VERIFICADOR] ❌ ERRO ao enviar log para o bot: {e}")

                            # Remove do JSON
                            del dados[payment_id]
                            salvar_dados(dados)
                        else:
                            print(f"[VERIFICADOR] ❌ Erro ao adicionar coins para {character_id}")

                except Exception as e:
                    print(f"[VERIFICADOR] ❌ Erro ao consultar pagamento {payment_id}: {e}")

        time.sleep(30)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Webhook do Mercado Pago está online com sucesso na porta {port}!")

    # Inicia o verificador automático em segundo plano
    threading.Thread(target=verificador_pendencias, daemon=True).start()

    app.run(host="0.0.0.0", port=port)

