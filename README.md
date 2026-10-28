# Guias Notificação

Notificador automático de vencimentos de guias via WhatsApp.

Lê uma Google Sheets e envia mensagem via Evolution API todo dia às 8h.
Avisa 3 dias antes e no dia do vencimento.

## Variáveis de ambiente (configurar no Railway)

| Variável | Descrição |
|---|---|
| `EVOLUTION_API_URL` | URL da sua instância Evolution API (ex: https://sua-instancia.railway.app) |
| `EVOLUTION_API_KEY` | Global API key da Evolution API |
| `EVOLUTION_INSTANCE` | Nome da instância criada |
| `DESTINO_WHATSAPP` | Número do destinatário com DDI (ex: 5511999990000) |
| `SPREADSHEET_ID` | ID da Google Sheets (parte da URL entre /d/ e /edit) |
| `GOOGLE_CREDS_JSON` | JSON completo da Service Account do Google |

## Rotas

- `GET /` — health check
- `GET /testar` — dispara a verificação manualmente (para testar)
