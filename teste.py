
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET

from brazilfiscalreport.danfe import Danfe

# Pastas do projeto
PASTA_XML = Path("XML")
PASTA_PDF = Path("PDF")
ARQUIVO_ZIP = Path("danfes.zip")

# Cria as pastas caso ainda não existam
PASTA_XML.mkdir(exist_ok=True)
PASTA_PDF.mkdir(exist_ok=True)


def identificar_modelo(caminho):
    """Identifica o modelo fiscal dentro do XML."""
    raiz = ET.parse(caminho).getroot()

    for elemento in raiz.iter():
        nome = elemento.tag.split("}")[-1]

        if nome == "ide":
            for filho in elemento:
                if filho.tag.split("}")[-1] == "mod":
                    return filho.text

    return None


arquivos_xml = sorted(PASTA_XML.glob("*.xml"))

print(f"Arquivos XML encontrados: {len(arquivos_xml)}")

if not arquivos_xml:
    print("Nenhum XML encontrado. Coloque os arquivos na pasta XML.")

elif len(arquivos_xml) > 500:
    print("Limite deste processo: 500 arquivos por execução.")

else:
    pdfs_gerados = []
    erros = []

    for numero, arquivo in enumerate(arquivos_xml, start=1):
        try:
            print(f"[{numero}/{len(arquivos_xml)}] Processando {arquivo.name}")

            # Verifica se é uma NF-e modelo 55
            modelo = identificar_modelo(arquivo)

            if modelo != "55":
                raise ValueError(
                    f"Modelo fiscal diferente de 55: {modelo}"
                )

            # Define o nome do PDF
            destino_pdf = PASTA_PDF / f"{arquivo.stem}.pdf"

            # Não converte se já existir PDF com o mesmo nome
            if destino_pdf.exists():
                print(
                    f"IGNORADO: {arquivo.name} - "
                    "PDF com a mesma nomenclatura já existe."
                )
                continue

            # Lê o XML e gera o DANFE
            conteudo_xml = arquivo.read_text(encoding="utf-8")
            danfe = Danfe(xml=conteudo_xml)
            danfe.output(str(destino_pdf))

            # Verifica se o PDF foi gerado corretamente
            if (
                not destino_pdf.is_file()
                or destino_pdf.stat().st_size == 0
            ):
                raise RuntimeError(
                    "O PDF não foi gerado corretamente."
                )

            pdfs_gerados.append(destino_pdf)
            print(f"PDF gerado: {destino_pdf}")

        except Exception as erro:
            erros.append((arquivo.name, str(erro)))
            print(f"ERRO em {arquivo.name}: {erro}")

    # Atualiza o ZIP com os PDFs gerados nesta execução
    if pdfs_gerados:
        with ZipFile(ARQUIVO_ZIP, "w", ZIP_DEFLATED) as zipf:
            for pdf in pdfs_gerados:
                zipf.write(pdf, arcname=pdf.name)

        print("\nCONVERSÃO FINALIZADA")
        print(f"PDFs gerados nesta execução: {len(pdfs_gerados)}")
        print(f"Arquivo ZIP: {ARQUIVO_ZIP.resolve()}")

    else:
        print("\nNenhum PDF novo foi gerado nesta execução.")

    # Registra os erros para consulta posterior
    if erros:
        print(f"\nArquivos com erro: {len(erros)}")

        with open(
            "erros_conversao.txt", "w", encoding="utf-8"
        ) as log:
            for nome, motivo in erros:
                log.write(f"{nome}: {motivo}\n")

        print("Detalhes salvos em erros_conversao.txt")

