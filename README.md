# 🚀 Automação de Extratos Bancários com Machine Learning

Este projeto automatiza a extração de transações bancárias a partir de **PDFs de extratos** e usa **Machine Learning** para categorizar os gastos automaticamente.  
Os dados são enviados para **Google Sheets**, permitindo um controle financeiro eficiente.  

---

## 📌 Funcionalidades

✅ **Leitura automática de PDFs de extratos**  
✅ **Classificação inteligente de transações usando Machine Learning**  
✅ **Evita lançamentos duplicados**  
✅ **Envia os dados automaticamente para Google Sheets**  
✅ **Pode ser integrado com APIs bancárias** (opcional)  

---

## 📷 Demonstração  

🔹 **Interface do Google Sheets com os dados lançados**  
![GOOGLE](https://github.com/user-attachments/assets/737eac41-5043-4e41-a807-7e5c7ce8446e)
🔹 **Saída do Terminal ao processar os PDFs**   
![TELAPDF](https://github.com/user-attachments/assets/57c1bffd-08dc-49ea-be2b-4d0124e6a3f9)
🔹 **PDF de extrato bancário processado**   
![EXTRAT](https://github.com/user-attachments/assets/ba176ff9-2d28-40ad-98a3-249072d9c66f)

---

## 🛠️ Tecnologias Usadas  

- **Python 3.10+**  
- **pandas, scikit-learn, joblib** (Machine Learning)  
- **gspread** (Google Sheets API)  
- **PyMuPDF** (Leitura de PDFs)  
- **requests** (Para futuras integrações com APIs bancárias)  

---

## 🚀 Como Usar  

### **1️⃣ Instalar dependências**  
```bash
pip install -r requirements.txt

2️⃣ Configurar o Google Sheets
Crie um Google Sheets e compartilhe com o e-mail da conta de serviço.
Salve o JSON das credenciais na pasta do projeto como credenciais.json.

3️⃣ Processar um PDF de Extrato Bancário
python atualizar_planilha.py
O script irá ler os PDFs na pasta extratos/, categorizar os gastos e atualizar a planilha automaticamente.

📡 Possíveis Melhorias
✅ Automatizar importação via API Bancária
✅ Criar um Dashboard interativo no Power BI
✅ Enviar notificações dos gastos no WhatsApp/Telegram
