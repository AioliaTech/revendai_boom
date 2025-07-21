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

def flatten_data(data):
    """
    Função para achatar estruturas de dados aninhadas e garantir que sempre tenhamos uma lista de dicionários
    """
    if not data:
        return []
    
    # Se é uma lista
    if isinstance(data, list):
        result = []
        for item in data:
            if isinstance(item, dict):
                result.append(item)
            elif isinstance(item, list):
                # Se o item é uma lista, recursivamente achatar
                result.extend(flatten_data(item))
            else:
                print(f"[AVISO] Item ignorado (tipo não suportado): {type(item)} - {item}")
        return result
    
    # Se é um dicionário
    elif isinstance(data, dict):
        return [data]
    
    else:
        print(f"[AVISO] Dados ignorados (tipo não suportado): {type(data)} - {data}")
        return []

def safe_get_value(item, keys, default=None):
    """
    Função segura para extrair valores de dicionários, tentando múltiplas chaves
    """
    if not isinstance(item, dict):
        return default
    
    if isinstance(keys, str):
        keys = [keys]
    
    for key in keys:
        if key in item and item[key] is not None:
            return item[key]
    
    return default

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
                response = requests.get(JSON_URL, timeout=30)
                response.raise_for_status()
                
                # Parse do JSON
                try:
                    data_dict = response.json()
                except json.JSONDecodeError as je:
                    print(f"[ERRO] JSON inválido na URL {JSON_URL}: {je}")
                    continue
                
                print(f"[DEBUG] Tipo de data_dict: {type(data_dict)}")
                
                # Extrair lista de veículos de forma mais robusta
                veiculos = []
                
                if isinstance(data_dict, list):
                    print(f"[DEBUG] JSON é uma lista direta com {len(data_dict)} itens")
                    veiculos = flatten_data(data_dict)
                    
                elif isinstance(data_dict, dict):
                    print(f"[DEBUG] JSON é um objeto com chaves: {list(data_dict.keys())}")
                    
                    # Tentar várias chaves possíveis para encontrar os veículos
                    possible_keys = ['veiculos', 'vehicles', 'data', 'items', 'results', 'content']
                    
                    for key in possible_keys:
                        if key in data_dict:
                            print(f"[DEBUG] Encontrou dados na chave '{key}'")
                            veiculos = flatten_data(data_dict[key])
                            break
                    
                    # Se não encontrou em nenhuma chave conhecida, tratar o próprio dict como veículo
                    if not veiculos and data_dict:
                        print(f"[DEBUG] Tratando objeto inteiro como veículo único")
                        veiculos = [data_dict]
                
                else:
                    print(f"[AVISO] Tipo de dados não suportado: {type(data_dict)}")
                    continue
                
                print(f"[INFO] Processando {len(veiculos)} veículos encontrados")
                
                # Processar cada veículo
                for i, v in enumerate(veiculos):
                    try:
                        # Verificação de segurança
                        if not isinstance(v, dict):
                            print(f"[AVISO] Veículo {i+1} não é um dicionário: {type(v)}")
                            continue
                        
                        # Extrair dados de forma segura
                        parsed = {
                            "id": safe_get_value(v, ["id", "ID", "codigo", "cod"]),
                            "tipo": safe_get_value(v, ["tipo", "type", "categoria_veiculo"]),
                            "versao": safe_get_value(v, ["versao", "version", "variant"]),
                            "marca": safe_get_value(v, ["marca", "brand", "fabricante"]),
                            "modelo": safe_get_value(v, ["modelo", "model", "nome"]),
                            "ano": safe_get_value(v, ["ano_mod", "anoModelo", "ano", "year_model", "ano_modelo"]),
                            "ano_fabricacao": safe_get_value(v, ["ano_fab", "anoFabricacao", "ano_fabricacao", "year_manufacture"]),
                            "km": safe_get_value(v, ["km", "quilometragem", "mileage", "kilometers"]),
                            "cor": safe_get_value(v, ["cor", "color", "colour"]),
                            "combustivel": safe_get_value(v, ["combustivel", "fuel", "fuel_type"]),
                            "cambio": safe_get_value(v, ["cambio", "transmission", "gear"]),
                            "motor": safe_get_value(v, ["motor", "engine", "motorization"]),
                            "portas": safe_get_value(v, ["portas", "doors", "num_doors"]),
                            "categoria": safe_get_value(v, ["categoria", "category", "class"]),
                            "cilindrada": safe_get_value(v, ["cilindrada", "displacement", "engine_size"]),
                            "preco": 0,
                            "opcionais": "",
                            "fotos": safe_get_value(v, ["galeria", "fotos", "photos", "images", "gallery"], [])
                        }
                        
                        # Inferir cilindrada se não estiver presente
                        if not parsed["cilindrada"]:
                            parsed["cilindrada"] = inferir_cilindrada(parsed["modelo"])
                        
                        # Tratar preço de forma mais robusta
                        preco_raw = safe_get_value(v, ["valor", "valorVenda", "preco", "price", "value"])
                        if preco_raw:
                            try:
                                if isinstance(preco_raw, str):
                                    # Remove caracteres não numéricos exceto ponto e vírgula
                                    preco_clean = ''.join(c for c in preco_raw if c.isdigit() or c in '.,')
                                    preco_clean = preco_clean.replace(',', '.')
                                    parsed["preco"] = float(preco_clean) if preco_clean else 0
                                else:
                                    parsed["preco"] = float(preco_raw)
                            except (ValueError, TypeError):
                                parsed["preco"] = 0
                        
                        # Tratar opcionais
                        opcionais_raw = safe_get_value(v, ["opcionais", "options", "extras", "features"])
                        if isinstance(opcionais_raw, list):
                            parsed["opcionais"] = ", ".join(str(item) for item in opcionais_raw if item)
                        elif opcionais_raw:
                            parsed["opcionais"] = str(opcionais_raw)
                        
                        # Garantir que fotos seja uma lista
                        if not isinstance(parsed["fotos"], list):
                            if parsed["fotos"]:
                                parsed["fotos"] = [parsed["fotos"]]
                            else:
                                parsed["fotos"] = []
                        
                        parsed_vehicles.append(parsed)
                        
                    except Exception as e:
                        print(f"[ERRO] Erro ao processar veículo {i+1}: {e}")
                        continue
                        
            except requests.RequestException as req_error:
                print(f"[ERRO] Erro de requisição para URL {JSON_URL}: {req_error}")
                continue
            except Exception as url_error:
                print(f"[ERRO] Erro geral na URL {JSON_URL}: {url_error}")
                continue

        # Criar resultado final
        data_dict = {
            "veiculos": parsed_vehicles,
            "_updated_at": datetime.now().isoformat(),
            "_total_count": len(parsed_vehicles)
        }

        # Salvar arquivo
        try:
            with open(JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=2)
            print(f"[OK] Arquivo {JSON_FILE} salvo com sucesso!")
        except Exception as save_error:
            print(f"[ERRO] Erro ao salvar arquivo: {save_error}")

        print(f"[OK] Dados atualizados com sucesso. Total de veículos: {len(parsed_vehicles)}")
        return data_dict

    except Exception as e:
        print(f"[ERRO GERAL] Falha ao converter JSON: {e}")
        # Retornar estrutura vazia em caso de erro
        return {
            "veiculos": [],
            "_updated_at": datetime.now().isoformat(),
            "_error": str(e)
        }

if __name__ == "__main__":
    result = fetch_and_convert_xml()
    total_vehicles = len(result.get('veiculos', []))
    print(f"Processamento concluído. {total_vehicles} veículos processados.")
    
    if total_vehicles > 0:
        print("\nPrimeiros 3 veículos processados:")
        for i, veiculo in enumerate(result['veiculos'][:3]):
            print(f"{i+1}. {veiculo.get('marca', 'N/A')} {veiculo.get('modelo', 'N/A')} - R$ {veiculo.get('preco', 0)}")
