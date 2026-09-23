from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase

from businesses.models import Business, Staff, WorkingHours
from services.models import Service

from .models import Appointment
from .services import (
    cancel_appointment,
    create_appointment,
    generate_slots,
    has_conflicting_appointment,
)

class AppointmentModelTests(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.customer = user_model.objects.create_user(
            username="customer",
            password="test-password",
        )

        self.owner = user_model.objects.create_user(
            username="owner",
            password="test-password",
            role=user_model.Role.BUSINESS_OWNER,
        )

        self.business = Business.objects.create(
            owner=self.owner,
            name="Test Business",
            phone="09120000000",
            address="Test Address",
        )

        self.service = Service.objects.create(
            business=self.business,
            name="Consultation",
            duration=30,
            price=100,
        )

        self.staff = Staff.objects.create(
            business=self.business,
            name="Test Staff",
        )

        self.staff.services.add(self.service)

        WorkingHours.objects.create(
            business=self.business,
            day_of_week=6,
            opening_time=time(9, 0),
            closing_time=time(18, 0),
        )

    def test_status_defaults_to_pending(self):
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            staff=self.staff,
            date=date(2026, 9, 20),
            start_time=time(10, 30),
        )

        self.assertEqual(
            appointment.status,
            Appointment.Status.PENDING,
        )

    def test_string_representation_contains_appointment_details(self):
        appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            staff=self.staff,
            date=date(2026, 9, 20),
            start_time=time(10, 30),
        )

        self.assertIn("customer", str(appointment))
        self.assertIn("Consultation", str(appointment))
        self.assertIn("2026-09-20", str(appointment))


class CreateAppointmentTests(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.customer = user_model.objects.create_user(
            username="customer",
            password="test-password",
        )

        self.owner = user_model.objects.create_user(
            username="owner",
            password="test-password",
            role=user_model.Role.BUSINESS_OWNER,
        )

        self.business = Business.objects.create(
            owner=self.owner,
            name="Test Business",
            phone="09120000000",
            address="Test Address",
        )

        self.service = Service.objects.create(
            business=self.business,
            name="Haircut",
            duration=60,
            price=100,
        )

        self.staff = Staff.objects.create(
            business=self.business,
            name="Sara",
        )

        self.staff.services.add(self.service)

        WorkingHours.objects.create(
            business=self.business,
            day_of_week=6,
            opening_time=time(9, 0),
            closing_time=time(18, 0),
        )

    def test_create_appointment_success(self):
        appointment = create_appointment(
            customer=self.customer,
            service=self.service,
            staff=self.staff,
            appointment_date=date(2026, 9, 20),
            start_time=time(12, 0),
        )

        self.assertEqual(Appointment.objects.count(), 1)
        self.assertEqual(appointment.customer, self.customer)
        self.assertEqual(appointment.service, self.service)
        self.assertEqual(appointment.staff, self.staff)

        self.assertEqual(
            appointment.date,
            date(2026, 9, 20),
        )

        self.assertEqual(
            appointment.start_time,
            time(12, 0),
        )

    def test_create_appointment_rejects_conflict(self):
        create_appointment(
            customer=self.customer,
            service=self.service,
            staff=self.staff,
            appointment_date=date(2026, 9, 20),
            start_time=time(12, 0),
        )

        with self.assertRaises(ValueError):
            create_appointment(
                customer=self.customer,
                service=self.service,
                staff=self.staff,
                appointment_date=date(2026, 9, 20),
                start_time=time(12, 30),
            )

        self.assertEqual(
            Appointment.objects.count(),
            1,

            create_appointment(
                customer=self.customer,
                service=self.service,
                staff=self.staff,
                appointment_date=date(2026, 9, 20),
                start_time=time(18, 0),
            )

        self.assertEqual(
            Appointment.objects.count(),
            0,
        )

    def test_create_appointment_rejects_unassigned_service(self):
        another_service = Service.objects.create(
            business=self.business,
            name="Massage",
            duration=60,
            price=200,
        )

        with self.assertRaises(ValueError):
            create_appointment(
                customer=self.customer,
                service=another_service,
                staff=self.staff,
                appointment_date=date(2026, 9, 20),
                start_time=time(12, 0),
            )

        self.assertEqual(
            Appointment.objects.count(),
            0,
        )

    def test_create_appointment_rejects_inactive_service(self):
        self.service.is_active = False
        self.service.save()

        with self.assertRaises(ValueError):
            create_appointment(
                customer=self.customer,
                service=self.service,
                staff=self.staff,
                appointment_date=date(2026, 9, 20),
                start_time=time(12, 0),
            )

        self.assertEqual(
            Appointment.objects.count(),
            0,
        )

    def test_create_appointment_rejects_inactive_staff(self):
        self.staff.is_active = False
        self.staff.save()

        with self.assertRaises(ValueError):
            create_appointment(
                customer=self.customer,
                service=self.service,
                staff=self.staff,
                appointment_date=date(2026, 9, 20),
                start_time=time(12, 0),
            )

        self.assertEqual(
            Appointment.objects.count(),
            0,
        )


class AvailabilityLogicTests(TestCase):
    def test_generate_slots_uses_30_minute_interval(self):
        slots = generate_slots(
            opening_time=time(9, 0),
            closing_time=time(12, 0),
            duration_minutes=60,
        )

        self.assertEqual(
            slots,
            [
                time(9, 0),
                time(9, 30),
                time(10, 0),
                time(10, 30),
                time(11, 0),
            ],
        )

    def test_generate_slots_does_not_exceed_closing_time(self):
        slots = generate_slots(
            opening_time=time(9, 0),
            closing_time=time(17, 0),
            duration_minutes=90,
        )

        self.assertNotIn(
            time(16, 0),
            slots,
        )

        self.assertIn(
            time(15, 30),
            slots,
        )

    def test_generate_slots_returns_empty_when_service_does_not_fit(self):
        slots = generate_slots(
            opening_time=time(9, 0),
            closing_time=time(10, 0),
            duration_minutes=90,
        )

        self.assertEqual(
            slots,
            [],
        )


class ConflictDetectionTests(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.customer = user_model.objects.create_user(
            username="customer",
            password="test-password",
        )

        self.owner = user_model.objects.create_user(
            username="owner",
            password="test-password",
            role=user_model.Role.BUSINESS_OWNER,
        )

        self.business = Business.objects.create(
            owner=self.owner,
            name="Test Business",
            phone="09120000000",
            address="Test Address",
        )

        self.service = Service.objects.create(
            business=self.business,
            name="Haircut",
            duration=60,
            price=100,
        )

        self.staff = Staff.objects.create(
            business=self.business,
            name="Sara",
        )

        self.staff.services.add(self.service)

        self.appointment_date = date(2026, 9, 20)

    def create_existing_appointment(
        self,
        start_time,
        status=Appointment.Status.CONFIRMED,
    ):
        return Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            staff=self.staff,
            date=self.appointment_date,
            start_time=start_time,
            status=status,
        )

    def test_overlapping_appointment_returns_true(self):
        self.create_existing_appointment(
            start_time=time(10, 0),
        )

        result = has_conflicting_appointment(
            staff=self.staff,
            appointment_date=self.appointment_date,
            start_time=time(10, 30),
            end_time=time(11, 30),
        )

        self.assertTrue(result)

    def test_adjacent_appointment_returns_false(self):
        self.create_existing_appointment(
            start_time=time(10, 0),
        )

        result = has_conflicting_appointment(
            staff=self.staff,
            appointment_date=self.appointment_date,
            start_time=time(11, 0),
            end_time=time(12, 0),
        )

        self.assertFalse(result)

    def test_separated_appointment_returns_false(self):
        self.create_existing_appointment(
            start_time=time(10, 0),
        )

        result = has_conflicting_appointment(
            staff=self.staff,
            appointment_date=self.appointment_date,
            start_time=time(12, 0),
            end_time=time(13, 0),
        )

        self.assertFalse(result)

    def test_cancelled_appointment_does_not_create_conflict(self):
        self.create_existing_appointment(
            start_time=time(10, 0),
            status=Appointment.Status.CANCELLED,
        )

        result = has_conflicting_appointment(
            staff=self.staff,
            appointment_date=self.appointment_date,
            start_time=time(10, 30),
            end_time=time(11, 30),
        )

        self.assertFalse(result)


class AvailabilityAPITests(APITestCase):
    def setUp(self):
        user_model = get_user_model()

        self.customer = user_model.objects.create_user(
            username="customer",
            password="test-password",
        )

        self.owner = user_model.objects.create_user(
            username="owner",
            password="test-password",
            role=user_model.Role.BUSINESS_OWNER,
        )

        self.business = Business.objects.create(
            owner=self.owner,
            name="Test Business",
            phone="09120000000",
            address="Test Address",
        )

        self.service = Service.objects.create(
            business=self.business,
            name="Haircut",
            duration=60,
            price=100,
        )

        self.staff = Staff.objects.create(
            business=self.business,
            name="Sara",
        )

        self.staff.services.add(self.service)

        WorkingHours.objects.create(
            business=self.business,
            day_of_week=6,
            opening_time=time(9, 0),
            closing_time=time(18, 0),
        )

    def test_available_slots_are_returned(self):
        response = self.client.get(
            f"/api/businesses/{self.business.id}/available-slots/",
            {
                "service_id": self.service.id,
                "staff_id": self.staff.id,
                "date": "2026-09-20",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            "09:00:00",
            response.json()["available_slots"],
        )

    def test_conflicting_slots_are_removed(self):
        Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            staff=self.staff,
            date=date(2026, 9, 20),
            start_time=time(10, 0),
            status=Appointment.Status.CONFIRMED,
        )

        response = self.client.get(
            f"/api/businesses/{self.business.id}/available-slots/",
            {
                "service_id": self.service.id,
                "staff_id": self.staff.id,
                "date": "2026-09-20",
            },
        )

        self.assertEqual(response.status_code, 200)

        available_slots = response.json()["available_slots"]

        self.assertNotIn("09:30:00", available_slots)
        self.assertNotIn("10:00:00", available_slots)
        self.assertNotIn("10:30:00", available_slots)

    def test_invalid_service_returns_404(self):
        response = self.client.get(
            f"/api/businesses/{self.business.id}/available-slots/",
            {
                "service_id": 999,
                "staff_id": self.staff.id,
                "date": "2026-09-20",
            },
        )

        self.assertEqual(response.status_code, 404)

    def test_invalid_date_returns_400(self):
        response = self.client.get(
            f"/api/businesses/{self.business.id}/available-slots/",
            {
                "service_id": self.service.id,
                "staff_id": self.staff.id,
                "date": "invalid-date",
            },
        )

        self.assertEqual(response.status_code, 400)


class AppointmentCreateAPITests(APITestCase):
    def setUp(self):
        user_model = get_user_model()

        self.customer = user_model.objects.create_user(
            username="customer",
            password="test-password",
        )

        self.owner = user_model.objects.create_user(
            username="owner",
            password="test-password",
            role=user_model.Role.BUSINESS_OWNER,
        )

        self.business = Business.objects.create(
            owner=self.owner,
            name="Test Business",
            phone="09120000000",
            address="Test Address",
        )

        self.service = Service.objects.create(
            business=self.business,
            name="Haircut",
            duration=60,
            price=100,
        )

        self.staff = Staff.objects.create(
            business=self.business,
            name="Sara",
        )

        self.staff.services.add(self.service)

        WorkingHours.objects.create(
            business=self.business,
            day_of_week=6,
            opening_time=time(9, 0),
            closing_time=time(18, 0),
        )

        self.other_owner = user_model.objects.create_user(
            username="other_owner",
            password="test-password",
            role=user_model.Role.BUSINESS_OWNER,
        )

        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Business",
            phone="09121111111",
            address="Other Address",
        )

        self.other_staff = Staff.objects.create(
            business=self.other_business,
            name="Other Staff",
        )

        self.client.force_authenticate(
            user=self.customer,
        )

    def test_create_appointment(self):
        response = self.client.post(
            "/api/appointments/",
            {
                "service_id": self.service.id,
                "staff_id": self.staff.id,
                "date": "2026-09-20",
                "start_time": "10:00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            Appointment.objects.count(),
            1,
        )

        appointment = Appointment.objects.first()

        self.assertEqual(
            appointment.customer,
            self.customer,
        )

        self.assertEqual(
            appointment.service,
            self.service,
        )

        self.assertEqual(
            appointment.staff,
            self.staff,
        )

        self.assertEqual(
            appointment.start_time,
            time(10, 0),
        )

    def test_create_appointment_rejects_conflict(self):
        Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            staff=self.staff,
            date=date(2026, 9, 20),
            start_time=time(10, 0),
            status=Appointment.Status.CONFIRMED,
        )

        response = self.client.post(
            "/api/appointments/",
            {
                "service_id": self.service.id,
                "staff_id": self.staff.id,
                "date": "2026-09-20",
                "start_time": "10:30",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            Appointment.objects.count(),
            1,
        )

    def test_cannot_create_appointment_with_staff_from_another_business(
        self,
    ):
        response = self.client.post(
            "/api/appointments/",
            {
                "service_id": self.service.id,
                "staff_id": self.other_staff.id,
                "date": "2026-09-20",
                "start_time": "10:00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertEqual(
            Appointment.objects.count(),
            0,
        )

    def test_anonymous_user_cannot_create_appointment(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            "/api/appointments/",
            {
                "service_id": self.service.id,
                "staff_id": self.staff.id,
                "date": "2026-09-20",
                "start_time": "10:00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertEqual(
            Appointment.objects.count(),
            0,
        )



class AppointmentCancelAPITests(APITestCase):
    def setUp(self):
        user_model = get_user_model()

        self.customer = user_model.objects.create_user(
            username="cancel_customer",
            password="test-password",
        )

        self.other_customer = user_model.objects.create_user(
            username="other_customer",
            password="test-password",
        )

        self.owner = user_model.objects.create_user(
            username="cancel_owner",
            password="test-password",
            role=user_model.Role.BUSINESS_OWNER,
        )

        self.other_owner = user_model.objects.create_user(
            username="other_owner",
            password="test-password",
            role=user_model.Role.BUSINESS_OWNER,
        )

        self.business = Business.objects.create(
            owner=self.owner,
            name="Cancel Test Business",
            phone="09120000000",
            address="Cancel Test Address",
        )

        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Business",
            phone="09121111111",
            address="Other Address",
        )

        self.service = Service.objects.create(
            business=self.business,
            name="Haircut",
            duration=60,
            price=100,
        )

        self.other_service = Service.objects.create(
            business=self.other_business,
            name="Other Service",
            duration=60,
            price=100,
        )

        self.staff = Staff.objects.create(
            business=self.business,
            name="Sara",
        )

        self.other_staff = Staff.objects.create(
            business=self.other_business,
            name="Other Staff",
        )

        self.staff.services.add(self.service)
        self.other_staff.services.add(self.other_service)

        self.appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            staff=self.staff,
            date=date(2026, 9, 20),
            start_time=time(10, 0),
            status=Appointment.Status.PENDING,
        )

    def test_customer_can_cancel_pending_appointment(self):
        self.client.force_authenticate(
            user=self.customer,
        )

        response = self.client.patch(
            f"/api/appointments/{self.appointment.id}/cancel/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.appointment.refresh_from_db()

        self.assertEqual(
            self.appointment.status,
            Appointment.Status.CANCELLED,
        )

    def test_customer_cannot_cancel_confirmed_appointment(self):
        self.appointment.status = Appointment.Status.CONFIRMED
        self.appointment.save()

        self.client.force_authenticate(
            user=self.customer,
        )

        response = self.client.patch(
            f"/api/appointments/{self.appointment.id}/cancel/",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.appointment.refresh_from_db()

        self.assertEqual(
            self.appointment.status,
            Appointment.Status.CONFIRMED,
        )

    def test_business_owner_can_cancel_pending_appointment(self):
        self.client.force_authenticate(
            user=self.owner,
        )

        response = self.client.patch(
            f"/api/appointments/{self.appointment.id}/cancel/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.appointment.refresh_from_db()

        self.assertEqual(
            self.appointment.status,
            Appointment.Status.CANCELLED,
        )

    def test_business_owner_can_cancel_confirmed_appointment(self):
        self.appointment.status = Appointment.Status.CONFIRMED
        self.appointment.save()

        self.client.force_authenticate(
            user=self.owner,
        )

        response = self.client.patch(
            f"/api/appointments/{self.appointment.id}/cancel/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.appointment.refresh_from_db()

        self.assertEqual(
            self.appointment.status,
            Appointment.Status.CANCELLED,
        )

    def test_other_customer_cannot_cancel_appointment(self):
        self.client.force_authenticate(
            user=self.other_customer,
        )

        response = self.client.patch(
            f"/api/appointments/{self.appointment.id}/cancel/",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.appointment.refresh_from_db()

        self.assertEqual(
            self.appointment.status,
            Appointment.Status.PENDING,
        )

    def test_other_business_owner_cannot_cancel_appointment(self):
        self.client.force_authenticate(
            user=self.other_owner,
        )

        response = self.client.patch(
            f"/api/appointments/{self.appointment.id}/cancel/",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.appointment.refresh_from_db()

        self.assertEqual(
            self.appointment.status,
            Appointment.Status.PENDING,
        )

    def test_customer_cannot_cancel_cancelled_appointment(self):
        self.appointment.status = Appointment.Status.CANCELLED
        self.appointment.save()

        self.client.force_authenticate(
            user=self.customer,
        )

        response = self.client.patch(
            f"/api/appointments/{self.appointment.id}/cancel/",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_business_owner_cannot_cancel_completed_appointment(self):
        self.appointment.status = Appointment.Status.COMPLETED
        self.appointment.save()

        self.client.force_authenticate(
            user=self.owner,
        )

        response = self.client.patch(
            f"/api/appointments/{self.appointment.id}/cancel/",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.appointment.refresh_from_db()

        self.assertEqual(
            self.appointment.status,
            Appointment.Status.COMPLETED,
        )

    def test_business_owner_cannot_cancel_no_show_appointment(self):
        self.appointment.status = Appointment.Status.NO_SHOW
        self.appointment.save()

        self.client.force_authenticate(
            user=self.owner,
        )

        response = self.client.patch(
            f"/api/appointments/{self.appointment.id}/cancel/",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.appointment.refresh_from_db()

        self.assertEqual(
            self.appointment.status,
            Appointment.Status.NO_SHOW,
        )

    def test_anonymous_user_cannot_cancel_appointment(self):
        self.client.force_authenticate(user=None)

        response = self.client.patch(
            f"/api/appointments/{self.appointment.id}/cancel/",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.appointment.refresh_from_db()

        self.assertEqual(
            self.appointment.status,
            Appointment.Status.PENDING,
        )

    def test_cancel_nonexistent_appointment_returns_404(self):
        self.client.force_authenticate(
            user=self.customer,
        )

        response = self.client.patch(
            "/api/appointments/999999/cancel/",
        )

        self.assertEqual(
            response.status_code,
            404,
        )