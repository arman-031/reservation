from datetime import date, datetime, timedelta

from businesses.models import WorkingHours

from .models import Appointment


def calculate_end_time(start_time, duration_minutes):
    start_datetime = datetime.combine(date.today(), start_time)

    end_datetime = start_datetime + timedelta(minutes=duration_minutes)

    return end_datetime.time()


def is_within_working_hours(working_hours, start_time, end_time):
    if working_hours.is_closed:
        return False

    if not working_hours.opening_time or not working_hours.closing_time:
        return False

    return (
        start_time >= working_hours.opening_time
        and end_time <= working_hours.closing_time
    )


def staff_can_perform_service(staff, service):
    return staff.services.filter(pk=service.pk).exists()


def has_conflicting_appointment(
    staff,
    appointment_date,
    start_time,
    end_time,
):
    appointments = Appointment.objects.filter(
        staff=staff,
        date=appointment_date,
        status__in=[
            Appointment.Status.PENDING,
            Appointment.Status.CONFIRMED,
        ],
    ).select_related("service")

    for appointment in appointments:
        existing_end_time = calculate_end_time(
            appointment.start_time,
            appointment.service.duration,
        )

        if (
            start_time < existing_end_time
            and end_time > appointment.start_time
        ):
            return True

    return False



def create_appointment(
    customer,
    service,
    staff,
    appointment_date,
    start_time,
):
    end_time = calculate_end_time(
        start_time,
        service.duration,
    )
    if not service.is_active:
        raise ValueError("Service is inactive.")

    if not staff.is_active:
        raise ValueError("Staff is inactive.")

    working_hours = WorkingHours.objects.filter(
        business=service.business,
        day_of_week=appointment_date.weekday(),
    ).first()

    if working_hours is None:
        raise ValueError("Business is closed on this day.")

    if not is_within_working_hours(
        working_hours,
        start_time,
        end_time,
    ):
        raise ValueError("Appointment is outside business working hours.")
    if staff.business_id != service.business_id:
        raise ValueError("Staff and service belong to different businesses.")

    if not staff_can_perform_service(staff, service):
        raise ValueError("Staff cannot perform this service.")
    if has_conflicting_appointment(
        staff,
        appointment_date,
        start_time,
        end_time,
):
        raise ValueError("Staff already has an appointment at this time.")
    appointment = Appointment.objects.create(
        customer=customer,
        service=service,
        staff=staff,
        date=appointment_date,
        start_time=start_time,
)

    return appointment



def generate_slots(
    opening_time,
    closing_time,
    duration_minutes,
    interval_minutes=30,
):
    slots = []

    current_datetime = datetime.combine(
        date.today(),
        opening_time,
    )

    closing_datetime = datetime.combine(
        date.today(),
        closing_time,
    )

    while (
        current_datetime
        + timedelta(minutes=duration_minutes)
        <= closing_datetime
    ):
        slots.append(current_datetime.time())

        current_datetime += timedelta(
            minutes=interval_minutes,
        )

    return slots