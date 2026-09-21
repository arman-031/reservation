from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from .models import Business, Staff, WorkingHours
from services.models import Service
from .models import Business, Staff


class StaffAPITestCase(APITestCase):
    def setUp(self):
        User = get_user_model()

        self.owner = User.objects.create_user(
            username="owner",
            password="testpass123",
            role="business_owner",
        )

        self.other_owner = User.objects.create_user(
            username="other_owner",
            password="testpass123",
            role="business_owner",
        )

        self.customer = User.objects.create_user(
            username="customer",
            password="testpass123",
            role="customer",
        )

        self.business = Business.objects.create(
            owner=self.owner,
            name="Test Salon",
            phone="09120000000",
            address="Test Address",
        )

        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Salon",
            phone="09121111111",
            address="Other Address",
        )

        self.staff = Staff.objects.create(
            business=self.business,
            name="Sara",
            phone="09122222222",
            is_active=True,
        )

        self.service = Service.objects.create(
            business=self.business,
            name="Hair Color",
            duration=60,
            price=500000,
            is_active=True,
        )

        self.service_2 = Service.objects.create(
            business=self.business,
            name="Keratin",
            duration=90,
            price=800000,
            is_active=True,
        )

        self.other_business_service = Service.objects.create(
            business=self.other_business,
            name="Haircut",
            duration=30,
            price=300000,
            is_active=True,
        )

    def test_business_owner_can_create_staff(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            f"/api/businesses/{self.business.id}/staff/",
            {
                "name": "Mina",
                "phone": "09123333333",
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

    def test_business_owner_can_create_staff_with_services(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            f"/api/businesses/{self.business.id}/staff/",
            {
                "name": "Mina",
                "phone": "09123333333",
                "is_active": True,
                "service_ids": [
                    self.service.id,
                    self.service_2.id,
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        staff = Staff.objects.get(
            business=self.business,
            name="Mina",
        )

        self.assertEqual(
            staff.services.count(),
            2,
        )

        self.assertTrue(
            staff.services.filter(
                id=self.service.id,
            ).exists()
        )

        self.assertTrue(
            staff.services.filter(
                id=self.service_2.id,
            ).exists()
        )

    def test_cannot_create_staff_with_service_from_another_business(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            f"/api/businesses/{self.business.id}/staff/",
            {
                "name": "Mina",
                "phone": "09123333333",
                "service_ids": [
                    self.service.id,
                    self.other_business_service.id,
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertFalse(
            Staff.objects.filter(
                business=self.business,
                name="Mina",
            ).exists()
        )

    def test_other_business_owner_cannot_create_staff(self):
        self.client.force_authenticate(user=self.other_owner)

        response = self.client.post(
            f"/api/businesses/{self.business.id}/staff/",
            {
                "name": "Unauthorized Staff",
                "phone": "09124444444",
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
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            f"/api/businesses/{self.business.id}/staff/",
            {
                "name": "Unauthorized Staff",
                "phone": "09125555555",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_cannot_create_staff(self):
        response = self.client.post(
            f"/api/businesses/{self.business.id}/staff/",
            {
                "name": "Unauthorized Staff",
                "phone": "09126666666",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_inactive_staff_is_not_visible_in_public_api(self):
        inactive_staff = Staff.objects.create(
            business=self.business,
            name="Inactive Staff",
            phone="09127777777",
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

    def test_active_staff_is_visible_in_public_api(self):
        response = self.client.get(
            f"/api/businesses/{self.business.id}/staff/"
        )

        self.assertEqual(response.status_code, 200)

        returned_ids = [
            staff["id"]
            for staff in response.data
        ]

        self.assertIn(
            self.staff.id,
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

    def test_business_owner_can_update_staff_services(self):
        self.staff.services.add(self.service)

        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            f"/api/businesses/{self.business.id}/staff/{self.staff.id}/",
            {
                "service_ids": [
                    self.service_2.id,
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.staff.refresh_from_db()

        self.assertEqual(
            self.staff.services.count(),
            1,
        )

        self.assertTrue(
            self.staff.services.filter(
                id=self.service_2.id,
            ).exists()
        )

        self.assertFalse(
            self.staff.services.filter(
                id=self.service.id,
            ).exists()
        )

    def test_patch_without_service_ids_keeps_existing_services(self):
        self.staff.services.add(
            self.service,
            self.service_2,
        )

        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            f"/api/businesses/{self.business.id}/staff/{self.staff.id}/",
            {
                "phone": "09128888888",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.staff.refresh_from_db()

        self.assertEqual(
            self.staff.services.count(),
            2,
        )

        self.assertTrue(
            self.staff.services.filter(
                id=self.service.id,
            ).exists()
        )

        self.assertTrue(
            self.staff.services.filter(
                id=self.service_2.id,
            ).exists()
        )

    def test_patch_with_empty_service_ids_removes_all_services(self):
        self.staff.services.add(
            self.service,
            self.service_2,
        )

        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            f"/api/businesses/{self.business.id}/staff/{self.staff.id}/",
            {
                "service_ids": [],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.staff.refresh_from_db()

        self.assertEqual(
            self.staff.services.count(),
            0,
        )

    def test_cannot_update_staff_with_service_from_another_business(self):
        self.staff.services.add(self.service)

        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            f"/api/businesses/{self.business.id}/staff/{self.staff.id}/",
            {
                "service_ids": [
                    self.other_business_service.id,
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.staff.refresh_from_db()

        self.assertTrue(
            self.staff.services.filter(
                id=self.service.id,
            ).exists()
        )

        self.assertFalse(
            self.staff.services.filter(
                id=self.other_business_service.id,
            ).exists()
        )

    def test_other_business_owner_cannot_update_staff(self):
        self.client.force_authenticate(user=self.other_owner)

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
            "09122222222",
        )

    def test_customer_cannot_update_staff(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.patch(
            f"/api/businesses/{self.business.id}/staff/{self.staff.id}/",
            {
                "phone": "09999999999",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_cannot_update_staff(self):
        response = self.client.patch(
            f"/api/businesses/{self.business.id}/staff/{self.staff.id}/",
            {
                "phone": "09999999999",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)



    class WorkingHoursAPITestCase(APITestCase):
    def setUp(self):
        User = get_user_model()

        self.owner = User.objects.create_user(
            username="working_hours_owner",
            password="testpass123",
            role="business_owner",
        )

        self.other_owner = User.objects.create_user(
            username="working_hours_other_owner",
            password="testpass123",
            role="business_owner",
        )

        self.customer = User.objects.create_user(
            username="working_hours_customer",
            password="testpass123",
            role="customer",
        )

        self.business = Business.objects.create(
            owner=self.owner,
            name="Working Hours Salon",
            phone="09120000000",
            address="Test Address",
        )

        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Working Hours Salon",
            phone="09121111111",
            address="Other Address",
        )

    def test_business_owner_can_create_working_hours(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            f"/api/businesses/{self.business.id}/working-hours/",
            {
                "day_of_week": 5,
                "opening_time": "09:00",
                "closing_time": "18:00",
                "is_closed": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        self.assertTrue(
            WorkingHours.objects.filter(
                business=self.business,
                day_of_week=5,
            ).exists()
        )

    def test_cannot_create_duplicate_working_hours_for_same_day(self):
        WorkingHours.objects.create(
            business=self.business,
            day_of_week=5,
            opening_time="09:00",
            closing_time="18:00",
            is_closed=False,
        )

        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            f"/api/businesses/{self.business.id}/working-hours/",
            {
                "day_of_week": 5,
                "opening_time": "10:00",
                "closing_time": "19:00",
                "is_closed": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            WorkingHours.objects.filter(
                business=self.business,
                day_of_week=5,
            ).count(),
            1,
        )

    def test_open_working_hours_require_opening_and_closing_time(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            f"/api/businesses/{self.business.id}/working-hours/",
            {
                "day_of_week": 5,
                "is_closed": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_opening_time_must_be_before_closing_time(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            f"/api/businesses/{self.business.id}/working-hours/",
            {
                "day_of_week": 5,
                "opening_time": "18:00",
                "closing_time": "09:00",
                "is_closed": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_closed_day_can_be_created_without_times(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            f"/api/businesses/{self.business.id}/working-hours/",
            {
                "day_of_week": 6,
                "is_closed": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        working_hours = WorkingHours.objects.get(
            business=self.business,
            day_of_week=6,
        )

        self.assertTrue(working_hours.is_closed)

    def test_working_hours_are_publicly_visible(self):
        WorkingHours.objects.create(
            business=self.business,
            day_of_week=5,
            opening_time="09:00",
            closing_time="18:00",
            is_closed=False,
        )

        response = self.client.get(
            f"/api/businesses/{self.business.id}/working-hours/"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["day_of_week"],
            5,
        )

    def test_working_hours_are_returned_ordered_by_day(self):
        WorkingHours.objects.create(
            business=self.business,
            day_of_week=1,
            opening_time="09:00",
            closing_time="18:00",
            is_closed=False,
        )

        WorkingHours.objects.create(
            business=self.business,
            day_of_week=5,
            opening_time="10:00",
            closing_time="16:00",
            is_closed=False,
        )

        response = self.client.get(
            f"/api/businesses/{self.business.id}/working-hours/"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data[0]["day_of_week"],
            1,
        )

        self.assertEqual(
            response.data[1]["day_of_week"],
            5,
        )

    def test_business_owner_can_update_working_hours(self):
        WorkingHours.objects.create(
            business=self.business,
            day_of_week=5,
            opening_time="09:00",
            closing_time="18:00",
            is_closed=False,
        )

        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            f"/api/businesses/{self.business.id}/working-hours/5/",
            {
                "closing_time": "20:00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        working_hours = WorkingHours.objects.get(
            business=self.business,
            day_of_week=5,
        )

        self.assertEqual(
            working_hours.closing_time.strftime("%H:%M"),
            "20:00",
        )

    def test_other_business_owner_cannot_update_working_hours(self):
        WorkingHours.objects.create(
            business=self.business,
            day_of_week=5,
            opening_time="09:00",
            closing_time="18:00",
            is_closed=False,
        )

        self.client.force_authenticate(user=self.other_owner)

        response = self.client.patch(
            f"/api/businesses/{self.business.id}/working-hours/5/",
            {
                "closing_time": "20:00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 404)

        working_hours = WorkingHours.objects.get(
            business=self.business,
            day_of_week=5,
        )

        self.assertEqual(
            working_hours.closing_time.strftime("%H:%M"),
            "18:00",
        )

    def test_customer_cannot_create_working_hours(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            f"/api/businesses/{self.business.id}/working-hours/",
            {
                "day_of_week": 5,
                "opening_time": "09:00",
                "closing_time": "18:00",
                "is_closed": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_cannot_create_working_hours(self):
        response = self.client.post(
            f"/api/businesses/{self.business.id}/working-hours/",
            {
                "day_of_week": 5,
                "opening_time": "09:00",
                "closing_time": "18:00",
                "is_closed": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)