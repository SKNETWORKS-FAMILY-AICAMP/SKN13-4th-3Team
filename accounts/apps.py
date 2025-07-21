from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    # 아래 ready 메소드를 추가합니다.
    def ready(self):
        import accounts.signals
