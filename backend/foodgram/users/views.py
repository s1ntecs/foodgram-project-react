from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .functions import create_access_token
from .models import User
from .serializers import AuthSerializer


@api_view(['POST'])
def auth(request):
    serializer = AuthSerializer(data=request.data)
    id_data = serializer.initial_data
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    try:
        email = id_data['email']
        password = id_data['password']
    except KeyError:
        raise ValidationError(
                {"errors": "поле 'email' и 'password' обязательны"}
            )
    user = get_object_or_404(
        User, email=email)

    if not user.password == password:
        data = {'error': 'wrong confirmation code'}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    user.confirmation_code = ''
    user.save()
    token = create_access_token(user)
    return Response(token)


@api_view(['POST'])
def logout(request):
    serializer = AuthSerializer(data=request.data)
    id_data = serializer.initial_data
    email = id_data['email']
    password = id_data['password']
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    user = get_object_or_404(
        User, email=email)

    if not user.password == password:
        data = {'error': 'wrong confirmation code'}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    user.confirmation_code = ''
    user.save()
    token = create_access_token(user)
    return Response(token)
