from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from car.models import Rent
from carrental import settings
from django.utils import timezone
from datetime import timedelta
import random
from django.template.loader import render_to_string

@shared_task(bind=True)
def test_func(self):
    # operations
    for i in range(10):
        print(i)
    return "Done"


@shared_task(bind=True)
def send_mail_func(self):
    users = get_user_model().objects.all()
    
    # timezone.localtime(users.created_at) + timedelta(days=2)

    #  to sent mail to multiple users

    for user in users:
        mail_subject = "Hi! Celery Testing"
        message = "Book Car for your trip with CarRental with few easy steps and Enjoy your trip!!"
        to_email = user.email
        send_mail(
            subject = mail_subject,
            message = message,
            from_email = settings.EMAIL_HOST_USER,
            recipient_list = [to_email],
            fail_silently = True,
        )

    return "Sent"


def generate_otp(length):
    otp = ""
    for _ in range(length):
        otp += str(random.randint(0, 9))
    return otp

@shared_task(bind=True)
def send_otp(self, to_email):
    length = 6
    otp = generate_otp(length)
    mail_subject = "OTP for your trip"
    context = {
            'otp': otp
        }
    html = render_to_string('email/send_otp.html', context)

    send_mail(
        subject = mail_subject,
        message = "Greatings of the day!",
        html_message = html,
        from_email = settings.EMAIL_HOST_USER,
        recipient_list = [to_email],
        fail_silently = True,
    )

    return "OTP Sent"

@shared_task(bind=True)
def send_receipt(self, to_email, rent_id):
    mail_subject = "Your Receipt is ready!!!"
    rent = Rent.objects.get(id=rent_id)
    context = {
        'rent': rent
    }

    html = render_to_string('email/booking_receipt.html', context)

    send_mail(
        subject = mail_subject,
        message = "Greatings of the day!",
        html_message = html,
        from_email = settings.EMAIL_HOST_USER,
        recipient_list = [to_email],
        fail_silently = True,
    )

    return "Receipt Sent"