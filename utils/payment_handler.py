import os
import uuid
import base64
import json
from io import BytesIO
from PIL import Image
import mercadopago

# SDK com token de produção
sdk = mercadopago.SDK("APP_USR-8739880550401490-062716-ce4741df8269258e6066355f9156772f-1972922133")

# Caminho para o arquivo de pagamentos pendentes
PAGAMENTOS_JSON = "pagamentos.json"

def salvar_pagamento(pagamento_id, account_id, valor, nome, sobrenome, cpf):
    dados = {}
    if os.path.exists(PAGAMENTOS_JSON):
        with open(PAGAMENTOS_JSON, "r", encoding="utf-8") as f:
            try:
                dados = json.load(f)
            except json.JSONDecodeError:
                dados = {}

    dados[str(pagamento_id)] = {
        "account_id": account_id,
        "valor": valor,
        "nome": nome,
        "sobrenome": sobrenome,
        "cpf": cpf
    }

    with open(PAGAMENTOS_JSON, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2)

def criar_pagamento_pix(valor, account_id, nome, sobrenome, cpf):
    referencia_unica = f"Account-{account_id}-TX-{uuid.uuid4()}"

    try:
        payment_data = {
            "transaction_amount": float(valor),
            "description": "Compra de Coins no Discord",
            "payment_method_id": "pix",
            "notification_url": "https://render-webhook-discord-mercadopago.onrender.com/webhook",  # Use HTTPS real com TLS 1.2+
            "external_reference": referencia_unica,
            "statement_descriptor": "DiscordCoins",
            "payer": {
                "email": f"{account_id}@example.com",
                "first_name": nome,
                "last_name": sobrenome,
                "identification": {
                    "type": "CPF",
                    "number": cpf
                }
            },
            "additional_info": {
                "items": [
                    {
                        "id": "coin_pack_1",
                        "title": "Pacote de Coins",
                        "description": "Pacote de recarga de coins no Discord",
                        "category_id": "virtual_goods",
                        "quantity": 1,
                        "unit_price": float(valor)
                    }
                ],
                "payer": {
                    "first_name": nome,
                    "last_name": sobrenome,
                    "registration_date": "2022-01-01T12:00:00.000-03:00"
                }
            }
        }

        response = sdk.payment().create(payment_data)
        data = response["response"]

        if response["status"] == 201:
            pagamento_id = data["id"]
            salvar_pagamento(pagamento_id, account_id, valor, nome, sobrenome, cpf)
            return {
                "id": pagamento_id,
                "qrcode_base64": data["point_of_interaction"]["transaction_data"]["qr_code_base64"],
                "qrcode": data["point_of_interaction"]["transaction_data"]["qr_code"]  # Adicionado para exibir código no embed
            }

        else:
            return {"message": data.get("message", "Erro desconhecido")}

    except Exception as e:
        return {"message": str(e)}
