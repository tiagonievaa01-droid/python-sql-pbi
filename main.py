import os
import glob
import shutil
from datetime import datetime
from csv_handler import carregar_dados_clientes
from freshservice_client import criar_ticket_enviar_boleto

# Configurações Principais
EMAIL_CONFIG_ID = 156000288508 
DIR_ENTRADA = "boletos_sap"
DIR_PROCESSADOS = "boletos_processados"

# NOME DO SEU ARQUIVO CSV (Altere se o seu arquivo tiver outro nome)
ARQUIVO_CSV = "Dados/base_clientes.csv" 

def gerar_relatorio_execucao(sucessos, falhas):
    """Gera um arquivo de texto com o resumo dos envios."""
    data_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_relatorio = f"relatorio_envios_{data_hora}.txt"
    
    with open(nome_relatorio, "w", encoding="utf-8") as f:
        f.write("==================================================\n")
        f.write(f"RELATÓRIO DE ENVIO DE BOLETOS - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("==================================================\n\n")
        
        f.write(f"TOTAL PROCESSADOS: {len(sucessos) + len(falhas)}\n")
        f.write(f"ENVIADOS COM SUCESSO: {len(sucessos)}\n")
        f.write(f"FALHAS/ERROS: {len(falhas)}\n\n")
        
        if sucessos:
            f.write("--- SUCESSOS ---\n")
            for item in sucessos:
                f.write(f"[OK] Pedido: {item['pedido']} | Cliente: {item['cliente']} | Email: {item['email']} | Ticket: #{item['ticket_id']}\n")
            f.write("\n")
            
        if falhas:
            f.write("--- FALHAS DE ENVIO ---\n")
            for item in falhas:
                f.write(f"[ERRO] Pedido: {item['pedido']} | Motivo: {item['motivo']}\n")
                
    print(f"\n📄 Relatório detalhado gerado: {nome_relatorio}")

def processar_boletos():
    os.makedirs(DIR_PROCESSADOS, exist_ok=True)
    
    print("📖 Carregando base de clientes...")
    # CORREÇÃO: Passando o nome do arquivo para a função
    df_clientes = carregar_dados_clientes(ARQUIVO_CSV)
    
    arquivos_pdf = glob.glob(os.path.join(DIR_ENTRADA, "*.pdf"))
    if not arquivos_pdf:
        print("ℹ️ Nenhum boleto encontrado para processar.")
        return

    print(f"🚀 Encontrados {len(arquivos_pdf)} boletos. Iniciando processamento...\n")
    
    sucessos = []
    falhas = []

    for filepath in arquivos_pdf:
        nome_arquivo = os.path.basename(filepath)
        pedido = os.path.splitext(nome_arquivo)[0]
        
        cliente_info = df_clientes[df_clientes['pedido'] == pedido]
        
        if cliente_info.empty:
            msg = f"Pedido '{pedido}' não encontrado na base CSV."
            print(f"⚠️ {msg}")
            falhas.append({"pedido": pedido, "motivo": msg})
            continue
            
        dados_cliente = cliente_info.iloc[0].to_dict()
        
        try:
            ticket_id = criar_ticket_enviar_boleto(filepath, dados_cliente, EMAIL_CONFIG_ID)
            
            # Move o arquivo processado e registra o sucesso
            shutil.move(filepath, os.path.join(DIR_PROCESSADOS, nome_arquivo))
            sucessos.append({
                "pedido": pedido,
                "cliente": dados_cliente['nome cliente'],
                "email": dados_cliente['email'],
                "ticket_id": ticket_id
            })
        except Exception as e:
            msg_erro = str(e)
            print(f"❌ Erro ao enviar pedido {pedido}: {msg_erro}")
            falhas.append({"pedido": pedido, "motivo": msg_erro})

    # Gera o relatório final de execução
    gerar_relatorio_execucao(sucessos, falhas)

if __name__ == "__main__":
    processar_boletos()