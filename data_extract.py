from selenium import webdriver
from bs4 import BeautifulSoup
import time
import mysql.connector
from datetime import datetime
import re

# URL da página com os resultados da Lotofácil
url = "https://loterias.caixa.gov.br/Paginas/Lotofacil.aspx"

# Configuração do MySQL
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "senha123",
    "auth_plugin": "mysql_native_password"
}

# Inicializa o driver do Selenium (certifique-se de ter o ChromeDriver instalado)
driver = webdriver.Chrome()

try:
    # Acessa a página
    driver.get(url)

    # Espera a página carregar completamente (ajuste o tempo se necessário)
    time.sleep(5)

    # Obtém o HTML da página após o carregamento do JavaScript
    html = driver.page_source

    # Analisa o HTML com Beautiful Soup
    soup = BeautifulSoup(html, "html.parser")

    # Extrai o número do concurso e a data
    concurso_data = soup.find("span", class_="ng-binding").text.strip()
    print(f"Dado capturado: {concurso_data}")

    # Extração robusta do número do sorteio
    try:
        numero_sorteios = int(concurso_data.split(" ")[1].replace("(", "").replace(")", ""))
    except (IndexError, ValueError):
        raise ValueError("Erro ao extrair o número do sorteios.")

    # Extração robusta da data
    data_match = re.search(r"\d{2}/\d{2}/\d{4}", concurso_data)
    if data_match:
        data = data_match.group(0)  # Pega a data no formato DD/MM/AAAA
        try:
            data_convertida = datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Erro ao converter a data: {data}.")
        print(f"Data convertida: {data_convertida}")
    else:
        raise ValueError("Data não encontrada no formato esperado.")

    # Extrai os números sorteados
    numeros_sorteados = [
        int(numero.text.strip())
        for numero in soup.find_all("li", class_="ng-binding dezena ng-scope")
    ]

    # Valida se 15 números foram encontrados
    if len(numeros_sorteados) != 15:
        raise ValueError(f"Números sorteados incompletos: {numeros_sorteados}")

    print(f"Números sorteados: {numeros_sorteados}")

    # Conexão com o MySQL
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Verifica se o banco de dados existe, caso contrário, cria
    cursor.execute("SHOW DATABASES")
    databases = [db[0] for db in cursor.fetchall()]
    if "loterias" not in databases:
        cursor.execute("CREATE DATABASE loterias")
        print("Banco de dados 'loterias' criado com sucesso.")

    # Conecta ao banco de dados criado
    conn.database = "loterias"

    # Criação da tabela (se não existir)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resultados_lotofacil (
            id INT AUTO_INCREMENT PRIMARY KEY,
            numero_concurso INT NOT NULL,
            data_sorteio DATE NOT NULL,
            numero_1 INT NOT NULL,
            numero_2 INT NOT NULL,
            numero_3 INT NOT NULL,
            numero_4 INT NOT NULL,
            numero_5 INT NOT NULL,
            numero_6 INT NOT NULL,
            numero_7 INT NOT NULL,
            numero_8 INT NOT NULL,
            numero_9 INT NOT NULL,
            numero_10 INT NOT NULL,
            numero_11 INT NOT NULL,
            numero_12 INT NOT NULL,
            numero_13 INT NOT NULL,
            numero_14 INT NOT NULL,
            numero_15 INT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY (numero_concurso)
        )
    """)

    # Verifica se o concurso já existe no banco de dados
    cursor.execute("SELECT COUNT(*) FROM resultados_lotofacil WHERE numero_concurso = %s", (numero_sorteios,))
    if cursor.fetchone()[0] > 0:
        print(f"Concurso {numero_sorteios} já existe no banco de dados. Ignorando inserção.")
    else:
        # Inserção dos dados no banco
        query = """
            INSERT INTO resultados_lotofacil (
                numero_concurso, data_sorteio, numero_1, numero_2, numero_3, numero_4, numero_5, numero_6, 
                numero_7, numero_8, numero_9, numero_10, numero_11, numero_12, numero_13, numero_14, numero_15
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (numero_sorteios, data_convertida, *numeros_sorteados))
        conn.commit()
        print("Dados inseridos com sucesso no banco de dados!")

except Exception as e:
    print(f"Erro: {e}")

finally:
    # Fecha a conexão com o banco e o navegador
    if 'conn' in locals() and conn.is_connected():
        conn.close()
    driver.quit()
