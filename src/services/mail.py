import os
from abc import ABC, abstractmethod


class EmailAdapter(ABC):
    @abstractmethod
    def send_activation_code(self, email: str, code: str) -> bool:
        pass


class ConsoleEmailAdapter(EmailAdapter):
    def send_activation_code(self, email: str, code: str) -> bool:
        print(f"📧 Sending activation code to {email}: {code}")
        return True


class HttpEmailAdapter(EmailAdapter):
    def __init__(self):
        # Use webhook.site to test (replace url)
        self.api_url = "https://my-third-party/api"
        self.api_key = os.getenv("MAIL_API_KEY", "change-this-key")

    def send_activation_code(self, email: str, code: str) -> bool:
        import json
        import urllib.request

        url = f"{self.api_url}/send"
        payload = {
            "to": email,
            "subject": "Activation Code",
            "body": f"Your code: {code}",
        }
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as response:
                return response.status == 200
        except Exception:
            return False


def get_email_adapter() -> EmailAdapter:
    return ConsoleEmailAdapter()
