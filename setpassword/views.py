from . import models
from django.http import (JsonResponse, HttpResponseNotFound,
                         HttpResponseForbidden, HttpResponseNotAllowed)
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@transaction.atomic
def setpassword(request, token):
    try:
        token = models.Token.objects.get(token=token)
    except models.Token.DoesNotExist:
        return HttpResponseNotFound()

    if not token.allow_reset and token.user.has_usable_password():
        return HttpResponseForbidden()

    if request.method == 'GET':
        return JsonResponse({'name': token.user.username,
                             'human_name': token.user.first_name + ' ' + token.user.last_name})
    elif request.method == 'POST':
        password = request.POST['password']
        user = token.user

        user.set_password(password)
        token.delete()
        user.save()
        return JsonResponse({'status': 'ok'})
    else:
        return HttpResponseNotAllowed()
