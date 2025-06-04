def fetch_and_convert_xml():
    try:
        if not XML_URL:
            raise ValueError("Variável XML_URL não definida")

        response = requests.get(XML_URL)
        data_list = xmltodict.parse(response.content)

        # Quando o XML já é uma lista direta, como no seu caso, convertemos manualmente
        # pois xmltodict coloca isso dentro de alguma chave se for XML tradicional
        # Mas você mencionou que o XML já está vindo praticamente em formato JSON (lista pura)

        # Se `data_list` vier como um dicionário com uma chave externa, extraia-a
        # Ex: {"veiculos": [ ... ] }
        # Caso esteja já em lista diretamente (como você mostrou), use diretamente
        if isinstance(data_list, dict):
            # Tentativa de detectar a lista de veículos (ex: {"veiculos": [ ... ]})
            for value in data_list.values():
                if isinstance(value, list):
                    data_list = value
                    break
            else:
                raise ValueError("Não foi possível localizar a lista de veículos no XML.")

        parsed_vehicles = []

        for v in data_list:
            try:
                parsed = {
                    "id": v.get("codigo_lk"),
                    "marca": v.get("marca"),
                    "modelo": v.get("modelo"),
                    "categoria": inferir_categoria(v.get("modelo")),
                    "ano": v.get("ano_modelo"),
                    "km": v.get("km"),
                    "cor": v.get("cor"),
                    "combustivel": v.get("combustivel"),
                    "cambio": v.get("cambio"),
                    "portas": v.get("numeroportas"),
                    "preco": converter_preco_xml(v.get("valor")),
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
        print(f"[ERRO] Falha ao converter XML: {e}")
        return {}
