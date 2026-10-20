import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()
FS_DOMAIN = os.getenv("FRESHSERVICE_DOMAIN")
FS_API_KEY = os.getenv("FRESHSERVICE_API_KEY")

EMAIL_CONFIG_ID_DEFAULT = os.getenv("EMAIL_CONFIG_ID", 156000288508)

def validar_email(email):
    """Verifica se o formato do e-mail é válido antes do envio."""
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(padrao, str(email).strip()) is not None

def criar_ticket_enviar_boleto(filepath, dados_cliente, email_config_id=EMAIL_CONFIG_ID_DEFAULT):
    email_destinatario = str(dados_cliente['email']).strip()
    
    # Validação de formato de e-mail
    if not validar_email(email_destinatario):
        raise ValueError(f"E-mail inválido ou mal formatado: '{email_destinatario}'")

    url = f"https://{FS_DOMAIN}.freshdesk.com/api/v2/tickets/outbound_email"
    
    # CORREÇÃO AQUI: 'id cliente' em minúsculas
    id_cliente = dados_cliente.get('id cliente', dados_cliente.get('ID cliente', ''))
    nome_cliente = dados_cliente.get('nome cliente', dados_cliente.get('nome', ''))
    pedido = dados_cliente.get('pedido', '')
    
    assunto = f"Envio de Boletos mistos aos clientes - {id_cliente}"
    
    texto_padrao = f"""
    Prezado cliente, {nome_cliente}<br>
    Segue anexo os boletos relacionados ao pedido {pedido}, de acordo com as notas fiscais já faturadas e entregues.<br><br>
    Se tiver alguma dúvida, estamos à disposição.<br>
    Entre em contato pelo WhatsApp (11) 95083-8179 ou, se preferir, ligue para 0800 770 8290.<br>
    #SorrisosQueGeramSorrisos<br>
    S.I.N. Implant System
    """
    
    data = {
        "email": email_destinatario,
        "cc_emails[]": "negociacao@sinimplantsystem.com",
        "subject": assunto,
        "description": texto_padrao,
        "status": 5,   # Fechado
        "priority": 1, # Baixa
        "source": 10,  # Outbound Email
        "type": "Envio de Boletos",
        "custom_fields[cf_categoria]": "Atendimento",
        "custom_fields[cf_subcategoria]": "Envio de Boletos",
        "email_config_id": int(email_config_id)
    }
    
    nome_arquivo_anexo = f"{nome_cliente}.pdf" 
    
    with open(filepath, 'rb') as f:
        files = [
            ('attachments[]', (nome_arquivo_anexo, f, 'application/pdf'))
        ]
        
        response = requests.post(url, auth=(FS_API_KEY, "X"), data=data, files=files)
        
        if response.status_code not in (200, 201):
            raise Exception(f"Falha na API ({response.status_code}): {response.text}")
            
        res_json = response.json()
        ticket_id = res_json.get("id", "Desconhecido")
        
        print(f"✅ Boleto enviado para {email_destinatario} | Ticket Freshdesk #{ticket_id}")
        return ticket_id