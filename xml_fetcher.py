import requests, json, os
from datetime import datetime
from unidecode import unidecode

JSON_FILE = "data.json"

MAPEAMENTO_CILINDRADAS = {
    "g 310": 300, "f 750 gs": 850, "f 850 gs": 850, "f 900": 900, "r 1250": 1250,
    "r 1300": 1300, "r 18": 1800, "k 1300": 1300, "k 1600": 1650, "s 1000": 1000,
    "g 650 gs": 650, "cb 300": 300, "cb 500": 500, "cb 650": 650, "cb 1000r": 1000,
    "cb twister": 300, "twister": 300, "cbr 250": 250, "cbr 500": 500, "cbr 600": 600,
    "cbr 650": 650, "cbr 1000": 1000, "hornet 600": 600, "cb 600f": 600, "xre 190": 190,
    "xre 300": 300, "xre 300 sahara": 300, "sahara 300": 300, "sahara 300 rally": 300,
    "nxr 160": 160, "bros 160": 160, "cg 160": 160, "cg 160 titan": 160, "cg 160 fan": 160,
    "cg 160 start": 160, "cg 160 titan s": 160, "cg 125": 125, "cg 125 fan ks": 125,
    "biz 125": 125, "biz 125 es": 125, "biz 110": 110, "pop 110": 110, "pop 110i": 110,
    "pcx 150": 150, "pcx 160": 160, "xj6": 600, "mt 03": 300, "mt 07": 690, "mt 09": 890,
    "mt 01": 1700, "fazer 150": 150, "fazer 250": 250, "ys 250": 250, "factor 125": 125,
    "factor 150": 150, "xtz 150": 150, "xtz 250": 250, "xtz 250 tenere": 250, "tenere 250": 250,
    "lander 250": 250, "yzf r3": 300, "yzf r-3": 300, "r15": 150, "r1": 1000,
    "nmax 160": 160, "xmax 250": 250, "gs500": 500, "bandit 600": 600, "bandit 650": 650,
    "bandit 1250": 1250, "gsx 650f": 650, "gsx-s 750": 750, "gsx-s 1000": 1000,
    "hayabusa": 1350, "gixxer 250": 250, "burgman 125": 125, "z300": 300, "z400": 400,
    "z650": 650, "z750": 750, "z800": 800, "z900": 950, "z1000": 1000, "ninja 300": 300,
    "ninja 400": 400, "ninja 650": 650, "ninja 1000": 1050, "ninja zx-10r": 1000,
    "er6n": 650, "versys 300": 300, "versys 650": 650, "xt 660": 660, "meteor 350": 350,
    "classic 350": 350, "hunter 350": 350, "himalayan": 400, "interceptor 650": 650,
    "continental gt 650": 650, "tiger 800": 800, "tiger 900": 900, "street triple": 750,
    "speed triple": 1050, "bonneville": 900, "trident 660": 660, "monster 797": 800,
    "monster 821": 820, "monster 937": 940, "panigale v2": 950, "panigale v4": 1100,
    "iron 883": 883, "forty eight": 1200, "sportster s": 1250, "fat bob": 1140,
    "road glide": 2150, "street glide": 1750, "next 300": 300, "commander 250": 250,
    "dafra citycom 300": 300, "dr 160": 160, "dr 160 s": 160, "cforce 1000": 1000,
    "trx 420": 420, "t350 x": 350, "xr300l tornado": 300, "fz25 fazer": 250, "fz15 fazer": 150,
    "biz es": 125, "elite 125": 125, "crf 230f": 230, "cg150 fan": 150, "cg150 titan": 150, "diavel 1260": 1260,
    "cg150 titan": 150, "YZF R-6": 600, "MT-03": 300, "MT03": 300, "ER-6N": 650, "xt 600": 600, "biz 125": 125,
    "cg 125": 125
}

# =================== UTILS =======================

def normalizar_modelo(modelo):
    if not modelo:
        return ""
    modelo_norm = unidecode(modelo).lower()
    modelo_norm = modelo_norm.replace(" ", "").replace("-", "").replace("_", "")
    return modelo_norm

def inferir_cilindrada(modelo):
    if not modelo:
        return None
    modelo_norm = normalizar_modelo(modelo)
    for mapeado, cilindrada in MAPEAMENTO_CILINDRADAS.items():
        mapeado_norm = normalizar_modelo(mapeado)
        if mapeado_norm in modelo_norm:
            return cilindrada
    return None

# =================== FETCHER MULTI-JSON =======================

def get_xml_urls():
    urls = []
    for var, val in os.environ.items():
        if var.startswith("XML_URL") and val:
            urls.append(val)
    if "XML_URL" in os.environ and os.environ["XML_URL"] not in urls:
        urls.append(os.environ["XML_URL"])
    return urls

def fetch_and_convert_xml():
    try:
        JSON_URLS = get_xml_urls()
        if not JSON_URLS:
            raise ValueError("Nenhuma variável XML_URL definida")

        parsed_vehicles = []

        for JSON_URL in JSON_URLS:
            print(f"[INFO] Processando URL: {JSON_URL}")
            try:
                response = requests.get(JSON_URL)
                response.raise_for_status()
                
                data_dict = response.json()
                
                print(f"[DEBUG] Tipo de data_dict: {type(data_dict)}")
                if isinstance(data_dict, list):
                    print(f"[DEBUG] É lista com {len(data_dict)} itens")
                    if len(data_dict) > 0:
                        print(f"[DEBUG] Primeiro item: {type(data_dict[0])}")
                else:
                    print(f"[DEBUG] É dict com chaves: {list(data_dict.keys()) if isinstance(data_dict, dict) else 'N/A'}")
                
                # Verifica se é uma lista direta ou se tem wrapper
                if isinstance(data_dict, list):
                    veiculos = data_dict  # JSON começa direto com lista
                else:
                    veiculos = data_dict.get("veiculos", [])  # JSON tem wrapper
                
                # Garante que seja lista
                if isinstance(veiculos, dict):
                    veiculos = [veiculos]
                
                print(f"[INFO] Encontrados {len(veiculos)} veículos")
                
                for v in veiculos:
                    try:
                        # Verifica se v é um dicionário
                        if not isinstance(v, dict):
                            print(f"[AVISO] Item não é dicionário: {type(v)} - {v}")
                            continue
                            
                        parsed = {
                            "id": v.get("id"),
                            "tipo": v.get("tipo"),
                            "versao": v.get("versao"),
                            "marca": v.get("marca"),
                            "modelo": v.get("modelo"),
                            "ano": v.get("ano_mod") or v.get("anoModelo") or v.get("ano"),
                            "ano_fabricacao": v.get("ano_fab") or v.get("anoFabricacao") or v.get("ano_fabricacao"),
                            "km": v.get("km"),
                            "cor": v.get("cor"),
                            "combustivel": v.get("combustivel"),
                            "cambio": v.get("cambio"),
                            "motor": v.get("motor"),
                            "portas": v.get("portas"),
                            "categoria": v.get("categoria"),
                            "cilindrada": v.get("cilindrada") or inferir_cilindrada(v.get("modelo")),
                            "preco": float(v.get("valor", 0)) if v.get("valor") else (v.get("valorVenda") or v.get("preco") or 0),
                            "opcionais": ", ".join(v.get("opcionais", [])) if isinstance(v.get("opcionais"), list) else v.get("opcionais"),
                            "fotos": v.get("galeria") or v.get("fotos") or []
                        }
                        parsed_vehicles.append(parsed)
                        
                    except Exception as e:
                        print(f"[ERRO ao converter veículo ID {v.get('id', 'N/A') if isinstance(v, dict) else 'N/A'}] {e}")
                        continue
                        
            except Exception as url_error:
                print(f"[ERRO na URL {JSON_URL}] {url_error}")
                continue

        data_dict = {
            "veiculos": parsed_vehicles,
            "_updated_at": datetime.now().isoformat()
        }

        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=2)

        print(f"[OK] Dados atualizados com sucesso. Total de veículos: {len(parsed_vehicles)}")
        return data_dict

    except Exception as e:
        print(f"[ERRO] Falha ao converter JSON: {e}")
        return {}

if __name__ == "__main__":
    result = fetch_and_convert_xml()
    print(f"Processamento concluído. {len(result.get('veiculos', []))} veículos processados.")
