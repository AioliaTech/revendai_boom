import requests, json, os
from datetime import datetime
from unidecode import unidecode

XML_URL = os.getenv("XML_URL")  # ou defina diretamente: XML_URL = "https://..."
JSON_FILE = "data.json"

# MAPEAMENTO_CATEGORIAS (mantido como no seu código original)
MAPEAMENTO_CATEGORIAS = {
    "d20": "Caminhonete", "tcross": "SUV", "c4": "Hatch", "T-": "SUV", "gol": "Hatch", "uno": "Hatch", "palio": "Hatch", "celta": "Hatch", "ka": "Hatch",
    "fiesta": "Hatch", "march": "Hatch", "sandero": "Hatch", "onix": "Hatch", "hb20": "Hatch",
    "i30": "Hatch", "golf": "Hatch", "polo": "Hatch", "fox": "Hatch", "up": "Hatch",
    "fit": "Hatch", "city": "Hatch", "yaris": "Hatch", "etios": "Hatch", "clio": "Hatch",
    "corsa": "Hatch", "bravo": "Hatch", "punto": "Hatch", "208": "Hatch", "argo": "Hatch",
    "mobi": "Hatch", "c3": "Hatch", "picanto": "Hatch", "astra hatch": "Hatch", "stilo": "Hatch",
    "focus hatch": "Hatch", "206": "Hatch", "c4 vtr": "Hatch", "kwid": "Hatch", "soul": "Hatch",
    "agile": "Hatch", "sonic hatch": "Hatch", "fusca": "Hatch",
    "civic": "Sedan", "corolla": "Sedan", "sentra": "Sedan", "versa": "Sedan", "jetta": "Sedan",
    "prisma": "Sedan", "voyage": "Sedan", "siena": "Sedan", "grand siena": "Sedan", "cruze": "Sedan",
    "cobalt": "Sedan", "logan": "Sedan", "fluence": "Sedan", "cerato": "Sedan", "elantra": "Sedan",
    "virtus": "Sedan", "accord": "Sedan", "altima": "Sedan", "fusion": "Sedan", "mazda3": "Sedan",
    "mazda6": "Sedan", "passat": "Sedan", "city sedan": "Sedan", "astra sedan": "Sedan", "vectra sedan": "Sedan",
    "classic": "Sedan", "cronos": "Sedan", "linea": "Sedan", "focus sedan": "Sedan", "ka sedan": "Sedan",
    "408": "Sedan", "c4 pallas": "Sedan", "polo sedan": "Sedan", "bora": "Sedan", "hb20s": "Sedan",
    "lancer": "Sedan", "camry": "Sedan", "onix plus": "Sedan",
    "duster": "SUV", "ecosport": "SUV", "hrv": "SUV", "compass": "SUV", "renegade": "SUV",
    "tracker": "SUV", "kicks": "SUV", "captur": "SUV", "creta": "SUV", "tucson": "SUV",
    "santa fe": "SUV", "sorento": "SUV", "sportage": "SUV", "outlander": "SUV", "asx": "SUV",
    "pajero": "SUV", "tr4": "SUV", "aircross": "SUV", "tiguan": "SUV", "t-cross": "SUV",
    "rav4": "SUV", "cx5": "SUV", "forester": "SUV", "wrx": "SUV", "land cruiser": "SUV",
    "cherokee": "SUV", "grand cherokee": "SUV", "xtrail": "SUV", "murano": "SUV", "cx9": "SUV",
    "edge": "SUV", "trailblazer": "SUV", "pulse": "SUV", "fastback": "SUV", "territory": "SUV",
    "bronco sport": "SUV", "2008": "SUV", "3008": "SUV", "c4 cactus": "SUV", "taos": "SUV",
    "cr-v": "SUV", "corolla ": "SUV", "sw4": "SUV", "pajero sport": "SUV", "commander": "SUV",
    "xv": "SUV", "xc60": "SUV", "tiggo 5x": "SUV", "haval h6": "SUV", "nivus": "SUV",
    "hilux": "Caminhonete", "ranger": "Caminhonete", "s10": "Caminhonete", "l200": "Caminhonete", "triton": "Caminhonete",
    "saveiro": "Utilitário", "strada": "Utilitário", "montana": "Utilitário", "oroch": "Utilitário",
    "toro": "Caminhonete", "frontier": "Caminhonete", "amarok": "Caminhonete", "gladiator": "Caminhonete",
    "maverick": "Caminhonete", "colorado": "Caminhonete", "dakota": "Caminhonete",
    "montana (nova)": "Caminhonete", "f-250": "Caminhonete", "courier (pickup)": "Caminhonete", "hoggar": "Caminhonete",
    "ram 1500": "Caminhonete",
    "kangoo": "Utilitário", "partner": "Utilitário", "doblo": "Utilitário", "fiorino": "Utilitário", "berlingo": "Utilitário",
    "express": "Utilitário", "combo": "Utilitário", "kombi": "Utilitário", "doblo cargo": "Utilitário", "kangoo express": "Utilitário",
    "master": "Furgão", "sprinter": "Furgão", "ducato": "Furgão", "daily": "Furgão", "jumper": "Furgão",
    "boxer": "Furgão", "trafic": "Furgão", "transit": "Furgão", "vito": "Furgão", "expert (furgão)": "Furgão",
    "jumpy (furgão)": "Furgão", "scudo (furgão)": "Furgão",
    "camaro": "Coupe", "mustang": "Coupe", "tt": "Coupe", "supra": "Coupe", "370z": "Coupe",
    "rx8": "Coupe", "challenger": "Coupe", "corvette": "Coupe", "veloster": "Coupe", "cerato koup": "Coupe",
    "clk coupe": "Coupe", "a5 coupe": "Coupe", "gt86": "Coupe", "rcz": "Coupe", "brz": "Coupe",
    "z4": "Conversível", "boxster": "Conversível", "miata": "Conversível", "beetle cabriolet": "Conversível", "slk": "Conversível",
    "911 cabrio": "Conversível", "tt roadster": "Conversível", "a5 cabrio": "Conversível", "mini cabrio": "Conversível", "206 cc": "Conversível",
    "eos": "Conversível",
    "spin": "Minivan", "livina": "Minivan", "caravan": "Minivan", "touran": "Minivan", "parati": "Station Wagon",
    "quantum": "Station Wagon", "sharan": "Minivan", "zafira": "Minivan", "picasso": "Minivan", "grand c4": "Minivan",
    "meriva": "Minivan", "scenic": "Minivan", "xsara picasso": "Minivan", "carnival": "Minivan", "idea": "Minivan",
    "spacefox": "Station Wagon", "golf variant": "Station Wagon", "palio weekend": "Station Wagon",
    "astra sw": "Station Wagon", "206 sw": "Station Wagon", "a4 avant": "Station Wagon", "fielder": "Station Wagon",
    "wrangler": "Off-road", "troller": "Off-road", "defender": "Off-road", "bronco": "Off-road", "samurai": "Off-road",
    "jimny": "Off-road", "land cruiser": "Off-road", "grand vitara": "Off-road", "jimny sierra": "Off-road", "bandeirante (ate 2001)": "Off-road"
}

def inferir_categoria(modelo):
    if not modelo:
        return None
    modelo_norm = unidecode(modelo).lower().replace("-", "").replace(" ", "").strip()
    for mapeado, categoria in MAPEAMENTO_CATEGORIAS.items():
        if mapeado in modelo_norm:
            return categoria
    return None

def converter_preco_xml(valor_str):
    if not valor_str:
        return None
    try:
        valor = str(valor_str).replace("R$", "").replace(".", "").replace(",", ".").strip()
        return float(valor)
    except ValueError:
        return None

def fetch_and_convert_json():
    try:
        if not XML_URL:
            raise ValueError("Variável XML_URL não definida")

        response = requests.get(XML_URL)
        response_json = response.json()  # <-- define aqui corretamente

        data_list = response_json.get("veiculos", [])

        if not isinstance(data_list, list):
            raise ValueError("Formato inesperado: esperado uma lista de veículos")

        parsed_vehicles = []

        for v in data_list:
            try:
                parsed = {
                    "id": v.get("id"),
                    "marca": v.get("marca"),
                    "modelo": v.get("modelo"),
                    "categoria": inferir_categoria(v.get("modelo")),
                    "ano": v.get("anoModelo"),
                    "km": v.get("km"),
                    "cor": v.get("cor"),
                    "combustivel": v.get("combustivel"),
                    "cambio": v.get("cambio"),
                    "portas": v.get("portas"),
                    "preco": converter_preco_xml(v.get("valorVenda")),
                    "preco": float(v.get("valorVenda", 0)),
                    "opcionais": v.get("opcionais"),
                    "fotos": v.get("fotos", [])
                }
                parsed_vehicles.append(parsed)
            except Exception as e:
                print(f"[ERRO ao converter veículo ID {v.get('codigo_lk')}] {e}")

        data_dict = {
            "veiculos": parsed_vehicles,
            "_updated_at": datetime.now().isoformat()
        }

        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=2)

        print("[OK] Dados atualizados com sucesso.")
        return data_dict

    except Exception as e:
        print(f"[ERRO] Falha ao converter JSON: {e}")
        return {}
