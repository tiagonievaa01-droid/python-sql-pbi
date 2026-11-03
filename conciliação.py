import pandas as pd
import glob

# Procura todos os arquivos Excel
arquivos = glob.glob("Dados/*.XLSX")

print("Arquivos encontrados:")
print(arquivos)

# Lista para armazenar os DataFrames
lista_dfs = []

# Lê cada arquivo
for arquivo in arquivos:
    print(f"Lendo: {arquivo}")
    df = pd.read_excel(arquivo)
    lista_dfs.append(df)

print("Todos os arquivos foram lidos.")

# Junta tudo
base_consolidada = pd.concat(lista_dfs, ignore_index=True)

print("\n===== INFORMAÇÕES DA BASE =====")
base_consolidada.info()

print("\n===== PRIMEIRAS 5 LINHAS =====")
print(base_consolidada.head())

# Salva o arquivo
base_consolidada.to_excel("base_consolidada.xlsx", index=False)

print("\nProjeto executado com sucesso!")

