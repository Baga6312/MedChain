from django.http import JsonResponse


def json_server_error(request):
    return JsonResponse({"detail": "Error while processing the request."}, status=500)

def json_not_found(request, exception=None):
    return JsonResponse({"detail": "Not found."}, status=404)