import secrets
import string

from django.conf import settings
from django.core.mail import send_mail


def create_confirmation_code():
    '''
    Генерирует код активации и возвращает его.

    В коде 9 случайных цифр.
    '''
    numbers = string.digits
    confirmation_code = ''.join(secrets.choice(numbers) for i in range(9))
    return confirmation_code


def send_signup_mail(user):
    '''
    Отправляет письмо на адрес пользователя с его кодом подтверждения.
    '''
    email = user.email
    confirmation_code = user.confirmation_code

    subject = 'Confirmation code'
    message = f'Ваш код подтверждения: {confirmation_code}'

    send_mail(
        subject,
        message,
        settings.EMAIL_ADMIN,
        [email],
        fail_silently=False,
    )
