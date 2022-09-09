from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    '''
    Разрешает доступ на запись админу и суперюзеру, остальным read-only.
    '''

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return user == user.is_admin


class AuthorOrAuthenticated(permissions.BasePermission):
    '''
    Дает право на просмотр аутентифицированным пользователям,
    и право на запись автору.
    '''

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
