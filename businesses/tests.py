from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import Business, Staff


class StaffAPITestCase(APITestCase):
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

        self.staff = Staff.objects.create(
            business=self.business,
            name="Sara",
            phone="09121111111",
            is_active=True,
        )

    def test_business_owner_can_create_staff(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            f"/api/businesses/{self.business.id}/staff/",
            {
                "name": "Mina",
                "phone": "09122222222",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        self.assertTrue(
            Staff.objects.filter(
                business=self.business,
                name="Mina",
            ).exists()
        )

    def test_other_business_owner_cannot_create_staff(self):
        User = get_user_model()

        other_owner = User.objects.create_user(
            username="other_owner",
            password="testpass123",
            role="business_owner",
        )

        self.client.force_authenticate(user=other_owner)

        response = self.client.post(
            f"/api/businesses/{self.business.id}/staff/",
            {
                "name": "Unauthorized Staff",
                "phone": "09123333333",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 404)

        self.assertFalse(
            Staff.objects.filter(
                business=self.business,
                name="Unauthorized Staff",
            ).exists()
        )

    def test_customer_cannot_create_staff(self):
        User = get_user_model()

        customer = User.objects.create_user(
            username="customer",
            password="testpass123",
            role="customer",
        )

        self.client.force_authenticate(user=customer)

        response = self.client.post(
            f"/api/businesses/{self.business.id}/staff/",
            {
                "name": "Unauthorized Staff",
                "phone": "09124444444",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_cannot_create_staff(self):
        response = self.client.post(
            f"/api/businesses/{self.business.id}/staff/",
            {
                "name": "Unauthorized Staff",
                "phone": "09125555555",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_inactive_staff_is_not_visible_in_public_api(self):
        inactive_staff = Staff.objects.create(
            business=self.business,
            name="Inactive Staff",
            phone="09126666666",
            is_active=False,
        )

        response = self.client.get(
            f"/api/businesses/{self.business.id}/staff/"
        )

        self.assertEqual(response.status_code, 200)

        returned_ids = [
            staff["id"]
            for staff in response.data
        ]

        self.assertNotIn(
            inactive_staff.id,
            returned_ids,
        )

    def test_business_owner_can_update_own_staff(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            f"/api/businesses/{self.business.id}/staff/{self.staff.id}/",
            {
                "phone": "09129999999",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.staff.refresh_from_db()

        self.assertEqual(
            self.staff.phone,
            "09129999999",
        )

    def test_other_business_owner_cannot_update_staff(self):
        User = get_user_model()

        other_owner = User.objects.create_user(
            username="other_owner",
            password="testpass123",
            role="business_owner",
        )

        self.client.force_authenticate(user=other_owner)

        response = self.client.patch(
            f"/api/businesses/{self.business.id}/staff/{self.staff.id}/",
            {
                "phone": "09999999999",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 404)

        self.staff.refresh_from_db()

        self.assertEqual(
            self.staff.phone,
            "09121111111",
        )