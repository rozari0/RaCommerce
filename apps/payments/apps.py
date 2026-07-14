from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    name = "apps.payments"

    def ready(self):
        import apps.payments.providers.stripe  # noqa: F401
        import apps.payments.providers.bkash  # noqa: F401
