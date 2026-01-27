import os
import smtplib
from email.message import EmailMessage
from typing import Dict, Iterable, Tuple

import pandas as pd
import streamlit as st

SUPPORT_EMAIL = "simohamedhadi05@gmail.com"
SUPPORT_PHONE = "+212 766052983"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME", SUPPORT_EMAIL)
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "jmoycgjedfqwulkg")


def append_to_excel(data: Dict[str, Iterable], filename: str = "utilisateurs.xlsx") -> bool:
    """Ajoute des données à un fichier Excel existant ou crée un nouveau fichier."""
    try:
        new_df = pd.DataFrame(data)

        if os.path.exists(filename):
            try:
                existing_df = pd.read_excel(filename)
                updated_df = pd.concat([existing_df, new_df], ignore_index=True)
            except Exception:
                st.warning(f"Création d'un nouveau fichier {filename}")
                updated_df = new_df
        else:
            updated_df = new_df

        updated_df.to_excel(filename, index=False)
        return True
    except Exception as exc:
        st.error(f"Erreur lors de l'enregistrement: {str(exc)}")
        return False


def send_email_safe(to_email: str, subject: str, body: str) -> Tuple[bool, str]:
    """Envoie un email avec gestion d'erreur robuste."""
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = SMTP_USERNAME
        msg["To"] = to_email

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        return True, "Email envoyé avec succès"
    except smtplib.SMTPAuthenticationError:
        return False, "Erreur d'authentification SMTP"
    except Exception as exc:
        return False, f"Erreur: {str(exc)}"
