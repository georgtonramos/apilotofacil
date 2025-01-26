import requests

# Configurações
BASE_URL = "http://127.0.0.1:8000"
USERNAME = "Viewer"
PASSWORD = "Senha,123!"

def obter_token(base_url, username, password):
    """Obtém o token JWT da API."""
    url = f"{base_url}/token"
    payload = {
        "username": username,
        "password": password
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"Token obtido com sucesso: {token}")
        return token
    else:
        print(f"Falha ao obter o token: {response.status_code} - {response.text}")
        return None

def listar_resultados(base_url, token):
    """Acessa a rota protegida /resultados."""
    url = f"{base_url}/resultados"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("Resultados:")
        print(response.json())
    else:
        print(f"Erro ao acessar /resultados: {response.status_code} - {response.text}")

def listar_resultado_por_concurso(base_url, token, concurso):
    """Acessa a rota protegida /resultados/{numero_concurso}."""
    url = f"{base_url}/resultados/{concurso}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print(f"Resultado do concurso {concurso}:")
        print(response.json())
    else:
        print(f"Erro ao acessar /resultados/{concurso}: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # Passo 1: Obter o token
    token = obter_token(BASE_URL, USERNAME, PASSWORD)
    if token:
        # Passo 2: Acessar /resultados
        listar_resultados(BASE_URL, token)

        # Passo 3: Acessar /resultados/{numero_concurso}
        numero_concurso = 1000  # Substitua por um número de concurso válido
        listar_resultado_por_concurso(BASE_URL, token, numero_concurso)