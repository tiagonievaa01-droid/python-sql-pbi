import pandas as pd
import os

def cruzar_dados_notas(caminho_csv, caminho_excel):
    print("🔄 Iniciando o cruzamento de dados...")
    
    try:
        # 1. Lê a base de clientes (CSV)
        df_csv = pd.read_csv(caminho_csv)
        
        # 2. Lê o relatório do sistema (Excel)
        print(f"📄 Lendo o arquivo Excel: {caminho_excel}")
        df_excel = pd.read_excel(caminho_excel)
        
        # Padroniza os nomes das colunas para evitar erros de espaços
        df_excel.columns = df_excel.columns.str.strip()
        df_csv.columns = df_csv.columns.str.strip()

        # 3. Agrupa as notas (referência) por pedido (n° pedido)
        # Transforma os valores em string, ignora os vazios e junta tudo com vírgula
        df_notas_agrupadas = df_excel.groupby('n° pedido')['referência'].apply(
            lambda x: ', '.join(x.dropna().astype(str).str.strip())
        ).reset_index()

        # 4. Faz o cruzamento (merge) usando o número do pedido
        df_final = pd.merge(df_csv, df_notas_agrupadas, how='left', left_on='pedido', right_on='n° pedido')

        # 5. Atualiza a coluna 'nota fiscal' no CSV
        if 'nota fiscal' in df_final.columns:
            # Substitui as notas apenas nos pedidos encontrados no Excel
            df_final['nota fiscal'] = df_final['referência'].fillna(df_final['nota fiscal'])
        else:
            # Cria a coluna caso ela não exista
            df_final['nota fiscal'] = df_final['referência']

        # Limpa as colunas auxiliares
        df_final = df_final.drop(columns=['n° pedido', 'referência'], errors='ignore')

        # 6. Salva o CSV atualizado por cima do antigo
        df_final.to_csv(caminho_csv, index=False)
        print("✅ Arquivo 'base_clientes.csv' atualizado com as notas agrupadas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante o cruzamento: {e}")

if __name__ == "__main__":
    ARQUIVO_CSV = "Dados/base_clientes.csv"
    
    # Atualizado para o nome exato do seu arquivo Excel
    ARQUIVO_EXCEL = "Dados/base.xlsx" 
    
    if not os.path.exists(ARQUIVO_CSV):
        print(f"⚠️ Arquivo CSV não encontrado: {ARQUIVO_CSV}")
    elif not os.path.exists(ARQUIVO_EXCEL):
        print(f"⚠️ Arquivo Excel não encontrado: {ARQUIVO_EXCEL}")
    else:
        cruzar_dados_notas(ARQUIVO_CSV, ARQUIVO_EXCEL)