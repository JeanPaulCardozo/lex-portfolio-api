import os
import resend
from dotenv import load_dotenv
from html import escape

load_dotenv()


def send_notification_email(to: str, subject: str, html: str) -> None:
    resend.api_key = os.getenv("EMAIL_API_KEY")
    resend.Emails.send(
        {
            "from": f"Lex Portfolio <{os.getenv('EMAIL_NO_REPLY')}>",
            "to": [to],
            "subject": subject,
            "html": html,
        }
    )


def build_contact_email_html(
    name: str, email: str, message: str, phone: str | None = None
) -> str:
    name, email, message = escape(name), escape(email), escape(message)
    phone_row = ""
    if phone:
        phone_row = f"""
        <tr>
          <td style="padding:6px 0;font-size:13px;color:#8a8a8a;">Teléfono</td>
          <td style="padding:6px 0;font-size:14px;color:#1c1c1c;">{escape(phone)}</td>
        </tr>"""

    return f"""
    <div style="font-family: Arial, Helvetica, sans-serif; max-width: 560px; margin: 0 auto; padding: 24px; background-color: #f7f5f2; border-radius: 12px;">
      <div style="background-color: #1c1c1c; color: #f5c77c; padding: 16px 24px; border-radius: 8px 8px 0 0; font-size: 18px; font-weight: bold;">
        Nuevo mensaje de contacto
      </div>
      <div style="background-color: #ffffff; padding: 24px; border-radius: 0 0 8px 8px; border: 1px solid #e5e0d8; border-top: none;">
        <p style="margin: 0 0 16px; font-size: 14px; color: #6b6b6b;">
          Alguien escribió a través del formulario de contacto de tu portafolio.
        </p>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
          <tr>
            <td style="padding: 6px 0; font-size: 13px; color: #8a8a8a; width: 90px;">Nombre</td>
            <td style="padding: 6px 0; font-size: 14px; color: #1c1c1c; font-weight: 600;">{name}</td>
          </tr>
         <tr>
            <td style="padding: 6px 0; font-size: 13px; color: #8a8a8a;">Correo</td>
            <td style="padding: 6px 0; font-size: 14px;">
                <a href="mailto:{email}" style="color: #b5792b; text-decoration: none;">{email}</a>
            </td>
        </tr>
          {phone_row}
        </table>
        <div style="background-color: #f7f5f2; border-left: 3px solid #d9ac4c; padding: 14px 16px; border-radius: 4px; font-size: 14px; line-height: 1.6; color: #333333; white-space: pre-wrap;">
          {message}
        </div>
        <div style="margin-top: 24px; text-align: center;">
          <a href="mailto:{email}?subject=Re:%20tu%20consulta"
             style="display: inline-block; background-color: #1c1c1c; color: #ffffff; padding: 10px 20px; border-radius: 24px; text-decoration: none; font-size: 13px; font-weight: 600;">
            Responder a {name}
          </a>
        </div>
      </div>
      <p style="text-align: center; font-size: 11px; color: #a0a0a0; margin-top: 16px;">
        Enviado automáticamente desde tu portafolio.
      </p>
    </div>
    """
