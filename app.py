import os
import requests
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime, date
import json

app = Flask(__name__)

# ── Configuração via variáveis de ambiente (definidas no Railway) ────────────
EVOLUTION_API_URL    = os.environ.get("EVOLUTION_API_URL")      # URL da sua instância
EVOLUTION_API_KEY    = os.environ.get("EVOLUTION_API_KEY")      # Global API key
EVOLUTION_INSTANCE   = os.environ.get("EVOLUTION_INSTANCE")     # Nome da instância
DESTINO_WHATSAPP     = os.environ.get("DESTINO_WHATSAPP")       # Ex: 5511999990000
SPREADSHEET_ID       = os.environ.get("SPREADSHEET_ID")         # ID da planilha
GOOGLE_CREDS_JSON    = os.environ.get("GOOGLE_CREDS_JSON")      # JSON da service account

SHEET_RANGE = "Painel de Guias!A4:I100"

# ── Google Sheets ─────────────────────────────────────────────────────────────
def get_sheet_data():
    creds_info = json.loads(GOOGLE_CREDS_JSON)
    creds = Credentials.from_service_account_info(
        creds_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    service = build("sheets", "v4", credentials=creds)
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_RANGE
    ).execute()
    return result.get("values", [])

def update_status(row_index, new_status):
    creds_info = json.loads(GOOGLE_CREDS_JSON)
    creds = Credentials.from_service_account_info(
        creds_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    service = build("sheets", "v4", credentials=creds)
    # Coluna G = índice 7 (Status), linha = row_index + 4 (offset do cabeçalho)
    cell = f"Painel de Guias!G{row_index + 4}"
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=cell,
        valueInputOption="RAW",
        body={"values": [[new_status]]}
    ).execute()

# ── WhatsApp via Evolution API ───────────────────────────────────────────────
def enviar_whatsapp(mensagem):
    url = f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE}"
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY
    }
    payload = {
        "number": DESTINO_WHATSAPP,
        "text": mensagem
    }
    response = requests.post(url, json=payload, headers=headers)
    print(f"WhatsApp status: {response.status_code} — {response.text}")

# ── Lógica principal ─────────────────────────────────────────────────────────
def verificar_vencimentos():
    print(f"Verificando vencimentos — {datetime.now()}")
    rows = get_sheet_data()
    hoje = date.today()

    hoje_lista  = []
    tres_lista  = []
    atrasadas   = []

    for i, row in enumerate(rows):
        if len(row) < 7:
            continue

        tipo       = row[2] if len(row) > 2 else ""
        venc_str   = row[3] if len(row) > 3 else ""
        valor      = row[4] if len(row) > 4 else ""
        onde_pagar = row[5] if len(row) > 5 else ""
        status     = row[6] if len(row) > 6 else ""
        imovel     = row[1] if len(row) > 1 else ""

        if not tipo or not venc_str:
            continue
        if status.lower() == "pago":
            continue

        try:
            # Aceita formatos DD/MM/YYYY ou YYYY-MM-DD
            if "/" in venc_str:
                data_venc = datetime.strptime(venc_str, "%d/%m/%Y").date()
            else:
                data_venc = datetime.strptime(venc_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        diff = (data_venc - hoje).days
        valor_str = f"R$ {float(valor.replace(',', '.')):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if valor else "valor a preencher"
        data_str  = data_venc.strftime("%d/%m/%Y")
        onde      = onde_pagar or "ver planilha"

        if diff < 0:
            atrasadas.append(f"🔴 *ATRASADO* — {tipo} ({imovel})\n   📅 Venceu em {data_str} | {valor_str}\n   📍 {onde}")
            update_status(i, "Em Atraso")
        elif diff == 0:
            hoje_lista.append(f"🚨 *VENCE HOJE* — {tipo} ({imovel})\n   💰 {valor_str}\n   📍 {onde}")
        elif diff == 3:
            tres_lista.append(f"⚠️ *Vence em 3 dias ({data_str})* — {tipo} ({imovel})\n   💰 {valor_str}\n   📍 {onde}")

    if not hoje_lista and not tres_lista and not atrasadas:
        print("Nenhum aviso para hoje.")
        return

    msg = f"🔔 *Controle de Guias — {hoje.strftime('%d/%m/%Y')}*\n\n"

    if atrasadas:
        msg += "━━━ EM ATRASO ━━━\n" + "\n\n".join(atrasadas) + "\n\n"
    if hoje_lista:
        msg += "━━━ VENCE HOJE ━━━\n" + "\n\n".join(hoje_lista) + "\n\n"
    if tres_lista:
        msg += "━━━ AVISO — 3 DIAS ━━━\n" + "\n\n".join(tres_lista) + "\n\n"

    msg += "_(marque como Pago na planilha após quitar)_"
    enviar_whatsapp(msg)

# ── Agendamento diário às 8h ─────────────────────────────────────────────────
scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")
scheduler.add_job(verificar_vencimentos, "cron", hour=8, minute=0)
scheduler.start()

# ── Rotas Flask ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return "Notificador de Guias — online ✅"

@app.route("/testar")
def testar():
    verificar_vencimentos()
    return "Verificação executada — confira o WhatsApp 📲"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
