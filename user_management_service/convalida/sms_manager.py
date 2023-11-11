from twilio.rest import Client
from db.logger import logger

# TWILIO_ACCOUNT_SID = "ACa378ac453d8f673195d24b7c7767f465"
# TWILIO_AUTH_TOKEN = "5a233bf4f320e1482c8dc299ffab3842"
# TWILIO_PHONE_NUMBER = ""

# client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# def send_sms(to, body):
#     message = client.messages.create(
#         to=to,
#         from_=TWILIO_PHONE_NUMBER,
#         body=body
#     )
#     return message.sid

###WHATSAPPP


def send_whatsapp(current_user, token,url_sito="http://localhost:8000"):
    prefix="+39"
    n_destinatario=(prefix+(current_user.n_telefono))
    print(n_destinatario)
    utente_nome = str(current_user.username)
    messaggio = (
    f"Subject:SoulAPP email\n\nBenvenuto a SOULCITY utente {utente_nome}, clicca sul link seguente"
    f"per convalidare la sua registrazione: {url_sito}/conferma_account?token={token}"
)
    
    account_sid = 'ACa378ac453d8f673195d24b7c7767f465'
    auth_token = '5a233bf4f320e1482c8dc299ffab3842'
    twilio_number= 'whatsapp:+14155238886'
    try:
        client = Client(account_sid, auth_token)
        messaggio = client.messages.create(
        from_=twilio_number,
        body=messaggio,
        to=f"whatsapp:{n_destinatario}"
        )
        return True
    except Exception as e:
        logger.error("Errore durante l'invio dell'messaggio per autenticare la registrazione: %s", e)
        return False    