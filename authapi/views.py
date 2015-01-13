from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.auth import authenticate

from . import models

def apiauth(func):
    def authenticator(request, *args, **kwargs):
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        error_response = HttpResponse('Unauthorized', status=401)
        error_response['WWW-Authenticate'] = 'Basic realm="API access"'
        if not auth.lower().startswith('basic '):
            return error_response
        password = auth[len('Basic '):].decode('base64').split(':')[1]
        if not models.APIKey.objects.filter(key=password).exists():
            return error_response
        return func(request, *args, **kwargs)

    return authenticator

@require_http_methods(['GET'])
@apiauth
def users(request):
    groups = {
        group.name: {
            'name': group.name,
            'gid': settings.BASE_GID + group.id,
            'members': []
        }
        for group in auth_models.Group.objects.all()
    }

    users = []
    for user in auth_models.User.objects.all().prefetch_related('groups'):
        for group in user.groups.all():
            groups[group.name]['members'].append(user.username)
        users.append({
            'name': user.username,
            'uid': settings.BASE_UID + user.id,
            'gid': settings.DEFAULT_GID,
            'home': settings.HOMEDIR_PATTERN % user.username,
            'shell': settings.DEFAULT_SHELL,
            'gecos': user.first_name + ' ' + user.last_name
        })

    return JsonResponse(
        {'status': 'ok', 'users': users, 'groups': groups.values()}
    )

@csrf_exempt
@require_http_methods(['POST'])
@apiauth
def auth(request):
    name = request.POST['name']
    password = request.POST['password']
    user = authenticate(username=name, password=password)

    if not user:
        return JsonResponse({'status': 'invalid_login'})
    if not user.is_active:
        return JsonResponse({'status': 'user_inactive'})

    return JsonResponse({'status': 'ok'})
