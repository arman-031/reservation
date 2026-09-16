from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from businesses.models import Business
from services.models import Service


class ServiceAPITestCase(APITestCase):
    def setUp(self):
        User = get_user_model()

        self.owner = User.objects.create_user(
            username="owner",
            password="testpass123",
            role="business_owner",
        )

        self.business = Business.objects.create(
            owner=self.owner,
            name="Test Salon",
            phone="09120000000",
            address="Test Address",
        )

        self.service = Service.objects.create(
            business=self.business,
            name="Hair Color",
            description="Hair coloring service",
            duration=60,
            price="200000",
            is_active=True,
        )

    def test_business_owner_can_create_service(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            f"/api/businesses/{self.business.id}/services/",
            {
                "name": "Hair Keratin",
                "description": "Hair keratin service",
                "duration": 90,
                "price": "300000",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_other_business_owner_cannot_create_service(self):
        User = get_user_model()

        other_owner = User.objects.create_user(
            username="other_owner",
            password="testpass123",
            role="business_owner",
        )

        self.client.force_authenticate(user=other_owner)

        response = self.client.post(
            f"/api/businesses/{self.business.id}/services/",
            {
                "name": "Unauthorized Service",
                "description": "Should not be created",
                "duration": 60,
                "price": "200000",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    def test_customer_cannot_create_service(self):
        User = get_user_model()

        customer = User.objects.create_user(
            username="customer",
            password="testpass123",
            role="customer",
        )

        self.client.force_authenticate(user=customer)

        response = self.client.post(
            f"/api/businesses/{self.business.id}/services/",
            {
                "name": "Unauthorized Service",
                "description": "Customer should not create this",
                "duration": 60,
                "price": "200000",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_cannot_create_service(self):
        response = self.client.post(
            f"/api/businesses/{self.business.id}/services/",
            {
                "name": "Unauthorized Service",
                "description": "Should not be created",
                "duration": 60,
                "price": "200000",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_inactive_service_is_not_visible_in_public_api(self):
        inactive_service = Service.objects.create(
            business=self.business,
            name="Inactive Service",
            description="This service should not be visible",
            duration=60,
            price="200000",
            is_active=False,
        )

        response = self.client.get(
            f"/api/businesses/{self.business.id}/services/"
        )

        self.assertEqual(response.status_code, 200)

        returned_ids = [
            service["id"]
            for service in response.data
        ]

        self.assertNotIn(
            inactive_service.id,
            returned_ids,
        )

    def test_business_owner_can_update_own_service(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            f"/api/businesses/{self.business.id}/services/{self.service.id}/",
            {
                "price": "250000",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.service.refresh_from_db()

        self.assertEqual(
            self.service.price,
            250000,
        )

    def test_other_business_owner_cannot_update_service(self):
        User = get_user_model()

        other_owner = User.objects.create_user(
            username="other_owner",
            password="testpass123",
            role="business_owner",
        )

        self.client.force_authenticate(user=other_owner)

        response = self.client.patch(
            f"/api/businesses/{self.business.id}/services/{self.service.id}/",
            {
                "price": "999999",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 404)

        self.service.refresh_from_db()

        self.assertEqual(
            self.service.price,
            200000,
        )




        