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

def salvar_pagamento(pagamento_id, character_id, valor, nome, sobrenome, cpf):
    print(f"[SALVAR] Iniciando salvamento do pagamento {pagamento_id}")
    dados = {}
    if os.path.exists(PAGAMENTOS_JSON):
        try:
            with open(PAGAMENTOS_JSON, "r", encoding="utf-8") as f:
                dados = json.load(f)
                print(f"[SALVAR] JSON carregado com sucesso: {len(dados)} registro(s)")
        except json.JSONDecodeError as e:
            print(f"[SALVAR] ⚠️ Erro ao carregar JSON: {e}")
            dados = {}
        except Exception as e:
            print(f"[SALVAR] ❌ Erro inesperado ao ler JSON: {e}")
            dados = {}

    dados[str(pagamento_id)] = {
        "character_id": character_id,
        "valor": valor,
        "nome": nome,
        "sobrenome": sobrenome,
        "cpf": cpf
    }

    try:
        with open(PAGAMENTOS_JSON, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2)
        print(f"[SALVAR] Pagamento {pagamento_id} salvo com sucesso!")
    except Exception as e:
        print(f"[SALVAR] ❌ Erro ao salvar JSON: {e}")

def criar_pagamento_pix(valor, character_id, nome, sobrenome, cpf):
    referencia_unica = f"Character-{character_id}-TX-{uuid.uuid4()}"
    print(f"[CRIAR] Iniciando criação de pagamento PIX para Character ID {character_id} | Valor: R${valor}")

    try:
        payment_data = {
            "transaction_amount": float(valor),
            "description": "Compra de Coins no Discord",
            "payment_method_id": "pix",
            "notification_url": "https://render-webhook-discord-mercadopago.onrender.com/webhook",
            "external_reference": referencia_unica,
            "statement_descriptor": "DiscordCoins",
            "payer": {
                "email": f"{character_id}@example.com",
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

        print(f"[CRIAR] Enviando pagamento para Mercado Pago...")
        response = sdk.payment().create(payment_data)
        data = response["response"]

        print(f"[CRIAR] Resposta recebida do Mercado Pago: {data.get('id')} | Status: {data.get('status')}")

        if response["status"] == 201:
            pagamento_id = data["id"]
            print(f"[CRIAR] Pagamento criado com sucesso. ID: {pagamento_id}")
            salvar_pagamento(pagamento_id, character_id, valor, nome, sobrenome, cpf)

            return {
                "id": pagamento_id,
                "qrcode_base64": data["point_of_interaction"]["transaction_data"]["qr_code_base64"],
                "qrcode": data["point_of_interaction"]["transaction_data"]["qr_code"]
            }

        else:
            erro = data.get("message", "Erro desconhecido")
            print(f"[CRIAR] ❌ Erro na criação do pagamento: {erro}")
            return {"message": erro}

    except Exception as e:
        print(f"[CRIAR] ❌ Exceção ao criar pagamento: {e}")
        return {"message": str(e)}
