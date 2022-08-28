from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    '''
    Разрешает доступ на запись админу и суперюзеру, остальным read-only.
    '''

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(request.user, 'is_admin', False)


class AdminModerAuthorOrReadOnly(permissions.BasePermission):
    '''
    Разрешает доступ к объекту автору, модератору, админу и суперюзеру.
    '''

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return (user == obj.author or user.is_moderator)


class AdminOrSuperuser(permissions.BasePermission):
    '''
    Разрешает доступ админу или суперюзеру.
    '''

    def has_permission(self, request, view):
        return getattr(request.user, 'is_admin', False)


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


class Authenticated(permissions.BasePermission):
    '''
    Дает право на запись аутентифицированным пользователям.
    '''
    message = "Adding customers not allowed."

    def has_permission(self, request, view):
        return request.user.is_authenticated


class Unauthorized(permissions.BasePermission):
    '''
    Разрешает доступ админу или суперюзеру.
    '''
    message = "You are already using the token."

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return False
        return True
