import secrets
import string

from django.conf import settings
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken


def create_confirmation_code():
    '''
    Генерирует код активации и возвращает его.

    В коде 9 случайных цифр.
    '''
    numbers = string.digits
    confirmation_code = ''.join(secrets.choice(numbers) for i in range(9))
    return confirmation_code


def create_access_token(user):
    '''
    Генерирует AccessToken для переданного пользователя.
    '''
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


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
