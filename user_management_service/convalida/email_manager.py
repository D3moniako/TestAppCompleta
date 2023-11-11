# ATTENZIONE IL FILE NON SI DEVE CHIAMARE EMAIL O AVRO' ERRORI DI IMPORT
import smtplib
from db.logger import logger

email_mia="soleroboo@gmail.com"
password_mia="mneezcmkrfxcpjxx" # devo usare quella di app password di google
# email_ricevente="soleroboo2@gmail.com"
countdown_conferma="5 ore"
# url_sito="http://localhost:8000"
def convalida_via_email(current_user, token, url_sito="http://localhost:8000"):
    email_ricevente = current_user.email
    utente_nome = str(current_user.username)
    messaggio = (
        f"Subject:SoulAPP email\n\nBenvenuto a SOULCITY utente {utente_nome}, clicca sul link seguente"
        f"per convalidare la sua registrazione: {url_sito}/conferma_account?token={token}"
    )
    connessione = smtplib.SMTP("smtp.gmail.com")

    try:
        connessione.starttls()
        connessione.login(user=email_mia, password=password_mia)
        
        # Invio email
        dati_inviati = connessione.sendmail(from_addr=email_mia, to_addrs=email_ricevente, msg=messaggio.encode('utf-8'))
        # Di default il messaggio è spedito in ASCII ma "è" non è ASCII, quindi devo codificare in utf
        logger.info("Email inviata con successo a %s. Risultato: %s", email_ricevente, dati_inviati)

        return True
    except Exception as e:
        logger.error("Errore durante l'invio dell'email per autenticare la registrazione: %s", e)
        return False
    finally:
        connessione.close()
