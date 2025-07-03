import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# Token do bot (seguro via variável de ambiente)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# ID do servidor vinculado ao bot
GUILD_ID = 1348029257963802684

# IDs de cargos
CARGOS = {
    "VISITANTE": 1349710870506373150,
    "MORADOR": 1349402937381748767,
    "AGUARDANDO": 1380534141224878171,
    "STAFF": 1380534770022223992,
    "ADVERTENCIA_1": 1380534373148917852,
    "ADVERTENCIA_2": 1380534491046608987,
    "LIBERACAO": 1348029636373905592,
    "DIRETOR": 1348029630275260459,
    "SUPORTE": 1380537207357575278,
    "DEVELOPER": 1349401347627159647,
    "RESP_ILEGAL": 1370781333814640751,
    "RESP_LEGAL": 1380538086051549317,
    "DIR_HOSPITAL": 1380538215831703755,
    "DIR_MECANICA": 1380538328960729198,
    "DIR_RESTAURANTE": 1380538562885189752,
    "MODERADOR": 1380539449921769482,
    "CEO": 1380539873668104245
}

# IDs de canais
CANAIS = {
    "AGUARDANDO": 1380531547899171048,
    "LOG_APROVADOS": 1380531651481702570,
    "APROVADOS": 1380531578605928488,
    "ALFANDEGA": 1380531886618706030,
    "LIBERACAO": 1380531789705248849,
    "CONEXAO": 1348029787750400091,
    "LOG_COMANDOS": 1380532170455515146,
    "WHITELIST": 1380531733987852388,
    "LOG_LIBERACAO": 1380532094521966612,
    "LOG_IMAGENS": 1380554805063454781,
    "LOG_ITENS_STAFF": 1384672607533662359,
    "CHAT_GERAL": 1352000926499737642,
    "log_comandos": 1384672607533662359,
    "LOG_COMPRAS": 1369852193389285416
}

# IDs de categorias
CATEGORIAS = {
    "WHITELIST": 1350173897194213440
}

# Configurações dos comandos
COMMANDS_CONFIG = {
    "teste": {
        "enabled": True,
        "allowed_roles": [
            CARGOS["STAFF"],
            CARGOS["DEVELOPER"],
            CARGOS["DIRETOR"],
            CARGOS["MODERADOR"]
        ]
    },
    "apagar": {
        "enabled": True,
        "allowed_roles": [
            CARGOS["STAFF"],
            CARGOS["MODERADOR"],
            CARGOS["DEVELOPER"],
            CARGOS["DIRETOR"]
        ]
    },
    "verificar": {
        "enabled": True,
        "allowed_roles": [
            CARGOS["DIRETOR"]
        ]
    },
    "verificar_captcha": {
        "enabled": True,
        "allowed_roles": []
    },
    "liberacao": {
        "enabled": True,
        "allowed_roles": [
            CARGOS["DIRETOR"],
            CARGOS["RESP_ILEGAL"]
        ]
    },
    "log_itens_listener": {
        "enabled": True,
        "allowed_roles": [
            CARGOS["STAFF"],
            CARGOS["DIRETOR"]
        ]
    },
    "log_admin_listener": {
        "enabled": True,
        "allowed_roles": [
            CARGOS["STAFF"],
            CARGOS["DIRETOR"]
        ]
    },
    "carregar": {
        "enabled": True,
        "allowed_roles": [
            CARGOS["SUPORTE"],
            CARGOS["DEVELOPER"]
        ]
    }
}
