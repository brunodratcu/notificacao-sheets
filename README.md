# Guias Notificação

Notificador automático de vencimentos de guias e impostos via WhatsApp.

Lê uma Google Sheets e envia mensagem via Z-API todo dia às 8h (horário de SP).
Avisa 3 dias antes e no dia do vencimento. Marca automaticamente como "Em Atraso" se passar da data.

## Variáveis de ambiente (configurar no Railway)

| Variável | Onde encontrar |
|---|---|
| `ZAPI_INSTANCE_ID` | Painel Z-API → sua instância → Instance ID |
| `ZAPI_TOKEN` | Painel Z-API → sua instância → Token |
| `ZAPI_CLIENT_TOKEN` | Painel Z-API → Security Token (no topo do painel) |
| `DESTINO_WHATSAPP` | Número do destinatário com DDI, sem + ou espaço (ex: `5511999990000`) |
| `SPREADSHEET_ID` | ID da Google Sheets — parte da URL entre `/d/` e `/edit` |
| `GOOGLE_CREDS_JSON` | JSON completo da Service Account do Google (cole o conteúdo inteiro) |

## Rotas

| Rota | Descrição |
|---|---|
| `GET /` | Health check — confirma que o app está online |
| `GET /testar` | Dispara a verificação manualmente (use para testar antes das 8h) |

## Como configurar (passo a passo)

### 1. Z-API
- Crie conta em [z-api.io](https://z-api.io)
- Crie uma instância e conecte o WhatsApp escaneando o QR Code
- Copie o Instance ID, Token e Client Token

### 2. Google Sheets API
- Acesse [console.cloud.google.com](https://console.cloud.google.com)
- Crie um projeto → ative a **Google Sheets API**
- Crie uma **Conta de Serviço** → gere uma chave **JSON**
- Compartilhe a planilha com o e-mail da conta de serviço (permissão de Editor)

### 3. Railway
- Conecte o repositório GitHub
- Em **Variables**, adicione todas as variáveis da tabela acima
- O app sobe automaticamente e roda todo dia às 8h

### 4. Testar
Acesse `https://sua-url.railway.app/testar` no browser para disparar manualmente e confirmar que o WhatsApp chegou.
