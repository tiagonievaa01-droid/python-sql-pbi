import pandas as pd
import glob
#procura todos os arquivos .xlsx dentro da pasta dados
arquivos = glob.glob("Dados/*.csv")

print(f"Total de arquivos encontrados: {len(arquivos)}")

#lista para armazenar os DataFrames
lista_dfs = []

#lê cada arquivo CSV
for arquivo in arquivos:
    print(f"Lendo: {arquivo}")

    df = pd.read_csv(
        arquivo,
        encoding="latin1",
        sep=None,
        engine="python",
        dtype=str
    )

    print(f"Linhas deste arquivo: {len(df)}")

    lista_dfs.append(df)

print(f"DataFrames na lista: {len(lista_dfs)}")
print("leitura concluida!") 

 #junta todos em um único DataFrame
base_consolidada = pd.concat(lista_dfs, ignore_index=True)

print("===== INFORMAÇÕES DA BASE =====")
base_consolidada.info()

print("\n===== NOMES DAS COLUNAS =====")
print(base_consolidada.columns)

print("\n===== TAMANHO DA BASE =====")
print(base_consolidada.shape)


    #exibe o resultado
print("\nBase consolidada:")
print(base_consolidada)

    #salva um novo arquivo excel
base_consolidada.to_csv(
    "base_consolidada.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nBase consolidada Arquivo 'base_consolidada.csv' criado com sucesso!")
