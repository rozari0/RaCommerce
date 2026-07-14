from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.orders.models import Order
from apps.products.models import Category, Product
from apps.users.models import User


class PaymentProcessorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            sku="TST-001",
            price=Decimal("25.00"),
            category=category,
            stock=10,
        )
        self.order = Order.objects.create(user=self.user)

    def add_item_to_order(self, quantity=2):
        from apps.orders.models import OrderItem

        return OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=quantity,
        )

    @patch("apps.payments.providers.stripe.stripe.checkout.Session.create")
    def test_stripe_checkout_returns_redirect_url(self, mock_stripe_session):
        self.add_item_to_order()
        mock_stripe_session.return_value = MagicMock(
            id="cs_test_123",
            url="https://checkout.stripe.com/pay/cs_test_123",
        )

        url = reverse("checkout", kwargs={"order_id": self.order.id})
        response = self.client.post(url, {"provider": "stripe"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("redirect_url", response.data)
        self.assertEqual(
            response.data["redirect_url"],
            "https://checkout.stripe.com/pay/cs_test_123",
        )
        self.assertIn("payment_id", response.data)

    def test_checkout_with_invalid_provider(self):
        self.add_item_to_order()
        url = reverse("checkout", kwargs={"order_id": self.order.id})
        response = self.client.post(url, {"provider": "invalid"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_checkout_unauthenticated(self):
        self.client.force_authenticate(user=None)
        self.add_item_to_order()
        url = reverse("checkout", kwargs={"order_id": self.order.id})
        response = self.client.post(url, {"provider": "stripe"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_checkout_order_not_found(self):
        url = reverse("checkout", kwargs={"order_id": 9999})
        response = self.client.post(url, {"provider": "stripe"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_checkout_already_paid_order(self):
        self.add_item_to_order()
        self.order.status = Order.STATUS_CHOICES.PAID
        self.order.save()

        url = reverse("checkout", kwargs={"order_id": self.order.id})
        response = self.client.post(url, {"provider": "stripe"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payment_status_view(self):
        from apps.payments.models import Payment

        self.add_item_to_order()
        payment = Payment.objects.create(
            order=self.order,
            amount=Decimal("50.00"),
            provider=Payment.Provider.STRIPE,
            transaction_id="cs_test_123",
        )

        url = reverse("payment-status", kwargs={"pk": payment.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], payment.id)
        self.assertEqual(response.data["status"], Payment.Status.PENDING)

    def test_bkash_provider_registered(self):
        from apps.payments.processors import PaymentProcessor

        processor = PaymentProcessor("bkash")
        self.assertIsNotNone(processor)

    @patch("apps.payments.providers.bkash.BkashProvider._get_client")
    def test_bkash_create_checkout(self, mock_get_client):
        self.add_item_to_order()

        mock_client = MagicMock()
        mock_client.create_payment.return_value = MagicMock(
            payment_id="TR0011test123",
            bkash_url="https://sandbox.bkash.com/checkout/TR0011test123",
        )
        mock_get_client.return_value = mock_client

        url = reverse("checkout", kwargs={"order_id": self.order.id})
        response = self.client.post(url, {"provider": "bkash"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("redirect_url", response.data)
        self.assertEqual(
            response.data["redirect_url"],
            "https://sandbox.bkash.com/checkout/TR0011test123",
        )
