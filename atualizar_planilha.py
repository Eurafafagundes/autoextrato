import os
import re
import fitz  # PyMuPDF para ler PDFs
import gspread
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials
import joblib  # Para carregar o modelo treinado

# ===== CONFIGURAÇÃO =====
CAMINHO_CREDENCIAIS = "aqui poem o endereço .json"
ID_PLANILHA = "aqui poem id da planilha google"
PASTA_EXTRATOS = "extratos"
ARQUIVO_PROCESSADOS = "processados.txt"  # Arquivo para armazenar PDFs já cadastrados
MODELO_ML = "modelo_categorizacao.pkl"  # Arquivo do modelo treinado

# ===== CARREGAR O MODELO DE MACHINE LEARNING =====
try:
    modelo = joblib.load(MODELO_ML)  # Carrega o modelo treinado
    vectorizer = joblib.load("vectorizer.pkl")  # Carrega o vetorizador corretamente
    print("✅ Modelo e Vetorizador carregados com sucesso!")
except Exception as e:
    print(f"❌ Erro ao carregar o modelo: {e}")
    exit()

# ===== AUTENTICAÇÃO NO GOOGLE SHEETS =====
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credenciais = Credentials.from_service_account_file(CAMINHO_CREDENCIAIS, scopes=scopes)
cliente = gspread.authorize(credenciais)
planilha = cliente.open_by_key(ID_PLANILHA)
aba = planilha.sheet1  # Primeira aba da planilha

# ===== FUNÇÃO PARA GERENCIAR PDFs JÁ PROCESSADOS =====
def carregar_pdfs_processados():
    if os.path.exists(ARQUIVO_PROCESSADOS):
        with open(ARQUIVO_PROCESSADOS, "r") as f:
            return set(f.read().splitlines())  # Retorna um conjunto de PDFs já processados
    return set()

def salvar_pdf_processado(nome_arquivo):
    with open(ARQUIVO_PROCESSADOS, "a") as f:
        f.write(nome_arquivo + "\n")  # Adiciona o nome do PDF ao histórico

# ===== FUNÇÃO PARA LIMPAR O TEXTO =====
def limpar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", "", texto)  # Remove pontuação
    palavras_irrelevantes = ["pix", "compra", "pagamento", "cartão", "fatura", "transação"]
    palavras = texto.split()
    palavras_filtradas = [palavra for palavra in palavras if palavra not in palavras_irrelevantes]
    return " ".join(palavras_filtradas)

# ===== FUNÇÃO PARA CLASSIFICAR AUTOMATICAMENTE USANDO MACHINE LEARNING =====
def categorizar_transacao(descricao):
    if not isinstance(descricao, str):  # Garante que a entrada seja uma string
        descricao = str(descricao)

    descricao_limpa = limpar_texto(descricao)  # Limpa o texto antes de classificar

    print(f"🔍 Vetorizando a descrição -> {descricao_limpa}")  # Debug para testar

    # Transforma a descrição em vetor
    try:
        descricao_transformada = vectorizer.transform([descricao_limpa])
        print(f"✅ Vetor gerado com sucesso -> {descricao_transformada.shape}")  # Debug
    except ValueError:
        print(f"⚠️ Erro: A descrição '{descricao_limpa}' contém palavras desconhecidas pelo modelo.")
        return "Outros"  # Se houver erro, retorna "Outros"

    # Converter csr_matrix para array antes da previsão
    descricao_transformada_array = descricao_transformada.toarray()

    # Faz a previsão da categoria corretamente
    try:
        categoria_prevista = modelo.predict(descricao_transformada_array)[0]
        print(f"✅ Previsão feita: {categoria_prevista}")  # Debug
    except Exception as e:
        print(f"❌ Erro ao prever categoria: {e}")
        return "Erro na previsão"

    return categoria_prevista  # Retorna a categoria prevista pelo modelo

# ===== FUNÇÃO PARA LER O CONTEÚDO DO PDF =====
def extrair_transacoes_pdf(caminho_pdf):
    doc = fitz.open(caminho_pdf)
    transacoes = []
    linhas_extracao = []

    for pagina in doc:
        texto = pagina.get_text("text")
        linhas = texto.split("\n")
        linhas_extracao.extend(linhas)

    for i in range(len(linhas_extracao) - 2):
        linha = linhas_extracao[i]
        ultima_linha = linhas_extracao[i + 2]  

        partes = linha.split()
        
        if len(partes) >= 2 and re.match(r"\d{2}/\d{2}/\d{4}", partes[0]):  
            data = partes[0]  
            descricao = " ".join(partes[1:]).lower()

            valor_str = ultima_linha.strip()
            valor_str = valor_str.replace(".", "").replace(",", ".")

            if not re.match(r"-?\d+\.\d+", valor_str):
                continue  

            valor = abs(float(valor_str))  

            # ===== CLASSIFICAÇÃO AUTOMÁTICA COM MACHINE LEARNING =====
            categoria = categorizar_transacao(descricao)

            transacoes.append([data, descricao.title(), categoria, valor])

    return transacoes

# ===== FUNÇÃO PARA ATUALIZAR A PLANILHA =====
def atualizar_planilha(novas_transacoes):
    if not novas_transacoes:
        print("Nenhuma nova transação para adicionar.")
        return

    novas_transacoes.sort(key=lambda x: datetime.strptime(x[0], "%d/%m/%Y"))

    aba.append_rows(novas_transacoes)
    print(f"{len(novas_transacoes)} novas transações adicionadas!")

# ===== EXECUÇÃO =====
def processar_pdfs():
    if not os.path.exists(PASTA_EXTRATOS):
        os.makedirs(PASTA_EXTRATOS)

    arquivos_pdfs = [f for f in os.listdir(PASTA_EXTRATOS) if f.endswith(".pdf")]

    if not arquivos_pdfs:
        print("Nenhum PDF encontrado na pasta.")
        return

    pdfs_processados = carregar_pdfs_processados()  # Carrega lista de PDFs já processados
    transacoes_existentes = set(tuple(linha[:3]) for linha in aba.get_all_values()[1:])
    novas_transacoes = []

    for arquivo in arquivos_pdfs:
        if arquivo in pdfs_processados:
            print(f"📌 {arquivo} já foi processado, pulando...")
            continue  # Pula o arquivo se já foi processado

        caminho_pdf = os.path.join(PASTA_EXTRATOS, arquivo)
        transacoes = extrair_transacoes_pdf(caminho_pdf)

        for transacao in transacoes:
            if tuple(map(str, transacao)) not in transacoes_existentes:
                novas_transacoes.append(transacao)

        salvar_pdf_processado(arquivo)  # Salva o PDF como processado após adicionar os dados

    atualizar_planilha(novas_transacoes)

# ===== CHAMANDO O PROCESSO =====
if __name__ == "__main__":
    processar_pdfs()
