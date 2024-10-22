import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from dotenv import load_dotenv





def process_document_result(result: AnalyzeResult, file_name: str) -> dict:

    """
    Processa o resultado da análise do documento e retorna um dicionário estruturado conforme especificado.

    Parâmetros:
    result (AnalyzeResult): O resultado da análise do documento.
    file_name (str): O nome do arquivo do documento.

    Retorna:
    dict: Um dicionário contendo informações estruturadas sobre o documento.
    """
    saida_json = {
        "documento": file_name,
        "totalPaginas": len(result.pages),
        "cabecalho": [],
        "tituloSecao": [],
        "ementa": [],
        "conteudo": [],
        "notaRodape": [],
        'totalPalavras': sum(len(page.words) for page in result.pages),
        'qtdTokens': round(sum(len(page.words) for page in result.pages) / 0.7, 2)
    }

    titulo_cabecalho_y = None
    coordenada_exclusao_y = 10.62

    for paragraph in result.paragraphs:
        pageNumber = paragraph.bounding_regions[0].page_number
        polygon = paragraph.bounding_regions[0].polygon

        y_superior_paragrafo = min(polygon[1], polygon[3])
        if y_superior_paragrafo > coordenada_exclusao_y:
            continue

        if paragraph.role == 'pageFooter' or paragraph.role == 'footnote':
            saida_json["notaRodape"].append({
                "texto": paragraph.content,
                "pagina": pageNumber,
                "coordenadas": polygon
            })

        elif paragraph.role in ['title', 'sectionHeading','pageHeader']:
            saida_json["tituloSecao"].append({
                "texto": paragraph.content,
                "pagina": pageNumber,
                "coordenadas": polygon
            })

        elif paragraph.role is None:
            if pageNumber == 1 and titulo_cabecalho_y is not None:
                y_inferior_paragrafo = min(polygon[1], polygon[3])
                if y_inferior_paragrafo < titulo_cabecalho_y:
                    saida_json['cabecalho'].append({
                        "texto": paragraph.content,
                        "pagina": pageNumber,
                        "coordenadas": polygon
                    })
                    continue
    
            saida_json["conteudo"].append({
                "texto": paragraph.content,
                "pagina": pageNumber,
                "coordenadas": polygon
            })

    # Ajuste da lógica para processar a ementa
    if saida_json["cabecalho"]:
        ultimo_paragrafo_ementa = saida_json["cabecalho"][-1]
        saida_json["ementa"].append(ultimo_paragrafo_ementa)
        saida_json["cabecalho"].pop()

    return saida_json



import re
import json

def extract_hex_string_from_filename(file_name):
    """
    Extrai uma string hexadecimal de 32 caracteres do nome do arquivo.

    Parâmetros:
    file_name (str): O nome do arquivo.

    Retorna:
    str: A string hexadecimal de 32 caracteres, se encontrada; caso contrário, None.
    """
    pattern = r'[A-F0-9]{32}'
    match = re.search(pattern, file_name)
    if match:
        return match.group(0)
    else:
        return None

def save_to_json(data, file_name, output_dir="."):
    # Remove a extensão .pdf do nome original do arquivo
    file_name = os.path.splitext(file_name)[0]
    # Define o nome do arquivo JSON com a extensão .json
    json_file_name = f"{file_name}.json"
    # Define o caminho completo do arquivo JSON
    json_file_path = os.path.join(output_dir, json_file_name)
    # Salva os dados em um arquivo JSON
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    return json_file_path