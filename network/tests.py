from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from network.models import (Factory, IndividualEntrepreneur, Product,
                            RetailNetwork)


class BaseNetworkTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", is_active=True
        )
        self.client.force_authenticate(user=self.user)

        # Создаем тестовые данные
        self.product = Product.objects.create(
            name="Test Product", model="Test Model", release_date="2023-01-01"
        )

        self.factory = Factory.objects.create(
            name="Test Factory",
            email="factory@test.com",
            country="Test Country",
            city="Test City",
            street="Test Street",
            house_number="123",
        )
        self.factory.products.add(self.product)

        # Получаем ContentType для Factory
        self.factory_content_type = ContentType.objects.get_for_model(Factory)


class FactoryTests(BaseNetworkTest):
    def test_factory_creation(self):
        self.assertEqual(self.factory.name, "Test Factory")
        self.assertEqual(self.factory.products.count(), 1)

    def test_factory_api_list(self):
        url = reverse("network:factory-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_factory_api_detail(self):
        url = reverse("network:factory-detail", args=[self.factory.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Factory")


class RetailNetworkTests(BaseNetworkTest):
    def setUp(self):
        super().setUp()
        self.retail_network = RetailNetwork.objects.create(
            name="Test Retail",
            email="retail@test.com",
            country="Test Country",
            city="Test City",
            street="Test Street",
            house_number="456",
            supplier_content_type=self.factory_content_type,
            supplier_object_id=self.factory.id,
        )
        self.retail_network.products.add(self.product)

    def test_retail_creation(self):
        self.assertEqual(self.retail_network.name, "Test Retail")
        self.assertEqual(self.retail_network.supplier, self.factory)
        self.assertEqual(self.retail_network.hierarchy_level, 1)

    def test_retail_api_create(self):
        url = reverse("network:retailnetwork-list")
        data = {
            "name": "New Retail",
            "email": "new@retail.com",
            "country": "Country",
            "city": "City",
            "street": "Street",
            "house_number": "789",
            "supplier_content_type": self.factory_content_type.id,
            "supplier_object_id": self.factory.id,
            "products": [self.product.id],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RetailNetwork.objects.count(), 2)


class IndividualEntrepreneurTests(BaseNetworkTest):
    def setUp(self):
        super().setUp()
        self.retail = RetailNetwork.objects.create(
            name="Parent Retail",
            email="parent@retail.com",
            country="Test Country",
            city="Test City",
            street="Test Street",
            house_number="456",
            supplier_content_type=self.factory_content_type,
            supplier_object_id=self.factory.id,
        )
        self.retail_content_type = ContentType.objects.get_for_model(RetailNetwork)

        self.entrepreneur = IndividualEntrepreneur.objects.create(
            name="Test Entrepreneur",
            email="entrepreneur@test.com",
            country="Test Country",
            city="Test City",
            street="Test Street",
            house_number="789",
            supplier_content_type=self.retail_content_type,
            supplier_object_id=self.retail.id,
        )
        self.entrepreneur.products.add(self.product)

    def test_entrepreneur_creation(self):
        self.assertEqual(self.entrepreneur.name, "Test Entrepreneur")
        self.assertEqual(self.entrepreneur.supplier, self.retail)
        self.assertEqual(self.entrepreneur.hierarchy_level, 2)

    def test_entrepreneur_api_update(self):
        url = reverse(
            "network:individualentrepreneur-detail", args=[self.entrepreneur.id]
        )
        data = {"name": "Updated Entrepreneur"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.entrepreneur.refresh_from_db()
        self.assertEqual(self.entrepreneur.name, "Updated Entrepreneur")


class ProductTests(BaseNetworkTest):
    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.model, "Test Model")

    def test_product_api_delete(self):
        new_product = Product.objects.create(
            name="To Delete", model="TD-123", release_date="2023-01-01"
        )
        url = reverse("network:product-detail", args=[new_product.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.filter(id=new_product.id).count(), 0)
