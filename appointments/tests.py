from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase

from businesses.models import Business
from services.models import Service

from .models import Appointment


class AppointmentModelTests(TestCase):
	def setUp(self):
		user_model = get_user_model()
		self.customer = user_model.objects.create_user(
			username="customer",
			password="test-password",
		)
		owner = user_model.objects.create_user(
			username="owner",
			password="test-password",
			role=user_model.Role.BUSINESS_OWNER,
		)
		business = Business.objects.create(
			owner=owner,
			name="Test Business",
		)
		self.service = Service.objects.create(
			business=business,
			name="Consultation",
			duration=30,
			price=100,
		)

	def test_status_defaults_to_pending(self):
		appointment = Appointment.objects.create(
			customer=self.customer,
			service=self.service,
			date=date(2026, 9, 15),
			start_time=time(10, 30),
		)

		self.assertEqual(appointment.status, Appointment.Status.PENDING)

	def test_string_representation_contains_appointment_details(self):
		appointment = Appointment.objects.create(
			customer=self.customer,
			service=self.service,
			date=date(2026, 9, 15),
			start_time=time(10, 30),
		)

		self.assertIn("customer", str(appointment))
		self.assertIn("Consultation", str(appointment))
		self.assertIn("2026-09-15", str(appointment))
