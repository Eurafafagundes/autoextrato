import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC  # Algoritmo atualizado para melhor precisão
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score
import joblib

# ===== CONFIGURAÇÃO =====
ARQUIVO_CSV = "historico_gastos.csv"  # Nome do arquivo CSV com dados categorizados

# ===== CARREGAR OS DADOS =====
df = pd.read_csv(ARQUIVO_CSV)

# Verifica se há colunas corretas no CSV
if "Descrição" not in df.columns or "Categoria" not in df.columns:
    raise ValueError("O CSV deve conter as colunas 'Descrição' e 'Categoria'!")

# ===== SEPARAR OS DADOS =====
X = df["Descrição"]  # Texto da descrição
y = df["Categoria"]  # Categoria associada

# Divide os dados para treino e teste (80% treino, 20% teste)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ===== CORREÇÃO DO ERRO: DEFINIR O MODELO ANTES DE USAR =====
stop_words_pt = [
    "de", "para", "em", "com", "por", "do", "da", "dos", "das", "no", "na",
    "os", "as", "um", "uma", "uns", "umas", "e", "ou", "se", "que", "a", "o"
]

modelo = make_pipeline(
    TfidfVectorizer(stop_words=stop_words_pt, ngram_range=(1,2), max_features=5000),
    SVC(kernel="linear", C=1.0)
)

# ===== TREINAR O MODELO =====
modelo.fit(X_train, y_train)  # ✅ Treina o modelo

# Testar o modelo antes de salvar
descricao_teste = ["PIX MERCADO EXTRA"]
try:
    # Não precisamos transformar manualmente a entrada, apenas chamamos predict()
    previsao_teste = modelo.predict(descricao_teste)[0]
    print(f"🔍 Teste de Previsão -> {previsao_teste}")
except Exception as e:
    print(f"❌ Erro ao prever a descrição de teste: {e}")

# Salvar separadamente o vetorizador e o modelo sem o pipeline completo
vectorizer = modelo.named_steps["tfidfvectorizer"]  # Extrai o vetorizador corretamente
modelo_sem_vectorizer = modelo.named_steps["svc"]  # Extrai apenas o classificador SVC

# Salvar os arquivos corretamente
joblib.dump(vectorizer, "vectorizer.pkl")  # Salva o vetor de palavras corretamente
joblib.dump(modelo_sem_vectorizer, "modelo_categorizacao.pkl")  # Agora salva apenas o classificador





# ===== TESTAR O MODELO =====
y_pred = modelo.predict(X_test)
acuracia = accuracy_score(y_test, y_pred)
print(f"🔍 Precisão do modelo: {acuracia:.2%}")

# ===== FUNÇÃO PARA CLASSIFICAR NOVAS TRANSAÇÕES =====
def prever_categoria(descricao):
    categoria_prevista = modelo.predict([descricao])[0]
    return categoria_prevista

# ===== TESTE COM NOVAS TRANSAÇÕES =====
testes = [
    "PIX MERCADO EXTRA",
    "COMPRA FARMÁCIA DROGASIL",
    "UBER VIAGEM",
    "PAGAMENTO CARTÃO MASTERCARD",
    "RESTAURANTE CHURRASCARIA",
]

print("\n🔹 Testando classificação automática:")
for teste in testes:
    print(f"'{teste}' → {prever_categoria(teste)}")
