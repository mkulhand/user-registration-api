import os
from abc import ABC, abstractmethod

from src.models import User


class MailSendError(Exception):
    detail = "Couldn't send mail"


class EmailAdapter(ABC):
    @abstractmethod
    def send_activation_code(self, user: User) -> None:
        pass


class InMemoryMailAdapter(EmailAdapter):
    mails: dict

    def send_activation_code(self, user: User) -> None:
        self.mails = {}
        user_data = user.to_snapshot()
        self.mails[user_data.get("email")] = {
            "type": "activation_code",
            "code": user_data.get("activation_code"),
        }

    def has_activation_code_mail(self, email: str, code: str) -> bool:
        mail = self.mails.get(email)

        return bool(mail and mail["type"] == "activation_code" and mail["code"] == code)


class ConsoleEmailAdapter(EmailAdapter):
    def send_activation_code(self, user: User) -> None:
        user_data = user.to_snapshot()
        print(
            f"""
############################################################################################
📧 Sending activation code to {user_data.get("email")}: {user_data.get("activation_code")}
############################################################################################
""",
            flush=True,
        )


class HttpEmailAdapter(EmailAdapter):
    def __init__(self):
        # Use webhook.site url to test
        self.api_url = "https://my-third-party/api/send"
        self.api_key = os.getenv("MAIL_API_KEY", "change-this-key")

    def send_activation_code(self, user: User) -> None:
        import json
        import urllib.request

        user_data = user.to_snapshot()
        payload = {
            "to": user_data.get("email"),
            "subject": "Activation Code",
            "body": f'Your code: {user_data.get("activation_code")}',
        }
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self.api_url}"
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as response:
                if response.status != 200:
                    raise Exception("Third-party mail provider failure")
        except Exception as e:
            raise MailSendError(e.detail)


def get_email_adapter() -> EmailAdapter:
    return (
        ConsoleEmailAdapter()
    )  # Change this to HttpEmailAdapter() to test mail request
