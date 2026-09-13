from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase

from businesses.models import Business, Staff, WorkingHours
from services.models import Service

from .models import Appointment
from .services import create_appointment


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
        self.assertEqual(appointment.date, date(2026, 9, 20))
        self.assertEqual(appointment.start_time, time(12, 0))

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

        self.assertEqual(Appointment.objects.count(), 1)

    def test_create_appointment_rejects_outside_working_hours(self):
        with self.assertRaises(ValueError):
            create_appointment(
                customer=self.customer,
                service=self.service,
                staff=self.staff,
                appointment_date=date(2026, 9, 20),
                start_time=time(18, 0),
            )

        self.assertEqual(Appointment.objects.count(), 0)

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

        self.assertEqual(Appointment.objects.count(), 0)

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

        self.assertEqual(Appointment.objects.count(), 0)

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

        self.assertEqual(Appointment.objects.count(), 0)