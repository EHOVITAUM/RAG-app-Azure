import os
import pandas as pd
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from dotenv import load_dotenv
from tqdm import tqdm
from functions import process_document_result, save_to_json

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()
key = os.getenv("DI_KEY")
endpoint = os.getenv("DI_ENDPOINT")
input_dir = os.getenv("INPUT_DIR")
log_file_path_csv = "iteration_log.csv"
log_file_path_pandas = "iteration_log.pkl"

# Verifica se as variáveis de ambiente foram carregadas corretamente
if not key or not endpoint or not input_dir:
    raise ValueError("Chave, endpoint ou diretório de entrada não encontrados. Certifique-se de que seu arquivo .env está configurado corretamente.")

# Cria e configura o cliente do Azure Document Intelligence
client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

# Verifica se o diretório de entrada existe
if not os.path.isdir(input_dir):
    raise ValueError("O diretório de entrada não existe.")

# CRIA um DataFrame do Pandas para armazenar o log
log_df = pd.DataFrame(columns=["file_name", "success"])

# Carrega o log anterior  (iteration_log.csv) se existir
if os.path.exists(log_file_path_csv):
    log_df = pd.read_csv(log_file_path_csv)

# Define uma lista para armazenar os nomes dos arquivos processados
arquivos_processados = log_df["file_name"].tolist()

# Define o contador de documentos processados
count = 0

# Cria a barra de progresso manualmente
qtde_iteracoes = int(input('quantos documentos deseja iterar ?'))
pbar = tqdm(total=qtde_iteracoes, desc="Processando arquivos", unit="arquivo")

while count< qtde_iteracoes:
    # Itera sobre os arquivos no diretório de entrada com uma barra de progresso
    for file_name in os.listdir(input_dir):
        # Verifica se o arquivo já foi processado
        if file_name in arquivos_processados:
            continue  # Pula para o próximo arquivo se este já foi processado 
        #pensar em lógica para capturar erro caso fique em loop
        #

        file_path = os.path.join(input_dir, file_name)

        # Verifica se é um arquivo
        if os.path.isfile(file_path):
            # Lê o documento PDF
            with open(file_path, "rb") as fd:
                document = fd.read()

            try:
                # raise Exception("Date provided can't be in the past")
                # Inicia a análise do documento
                poller = client.begin_analyze_document("prebuilt-layout", document, content_type="application/pdf")
                result = poller.result()

                # Processa o resultado da análise do documento
                saida_json = process_document_result(result, file_name)

                # Salva os dados em um arquivo JSON
                output_dir = os.getenv("OUTPUT_DIR", ".")
                output_file = save_to_json(saida_json, file_name, output_dir)

                # Adiciona o nome do arquivo ao log como bem sucedido
                log_df = log_df._append({"file_name": file_name, "success": True}, ignore_index=True)

                arquivos_processados.append(file_name)

                with open("logs-de-docs-processados.txt", "w") as arquivo:
                    for item in arquivos_processados:
                        arquivo.write(item + "/n")
            

                #estava fora do loop, testando dentro do loop
                # Salva o log em um arquivo CSV
                log_df.to_csv(log_file_path_csv, index=False)

                # Salva o log em um arquivo pickle do Pandas
                log_df.to_pickle(log_file_path_pandas)

            except Exception as e:
                # Adiciona o nome do arquivo ao log como falha
                log_df = log_df._append({"file_name": file_name, "success": False}, ignore_index=True)

            # Incrementa o contador de documentos processados
            count += 1
            pbar.update(1)  # Atualiza a barra de progresso
            if count >= qtde_iteracoes:
                break



# Fecha a barra de progresso
pbar.close()

# # Salva o log em um arquivo CSV
# log_df.to_csv(log_file_path_csv, index=False)

# # Salva o log em um arquivo pickle do Pandas
# log_df.to_pickle(log_file_path_pandas)

# print(log_df)
print(len(log_df))

# for arq in arquivos_processados:
#     print(f'{arq} \n')
# print("qtd arq processados: ",len(arquivos_processados))
# print("FIM DO PROGRAMA")