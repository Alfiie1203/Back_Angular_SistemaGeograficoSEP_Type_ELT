import yaml
import msal
import requests
from .models import Token
from django.http import HttpResponse

from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers.token_serializer import TokenSerializer


def landing_view(request):
    html_message = "<html><body><h1>this is an app landing</h1></body></html>"
    response = HttpResponse(html_message)
    return response



@permission_classes([IsAuthenticated])
class ReturnTokenView(APIView):
    queryset = Token.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            token = Token.objects.latest()
            serializer = TokenSerializer(token)
            return Response(serializer.data)
        except:
            return Response(
                {

                    "type": "validation_error",
                    "errors": [
                        {
                            "code": "not_found",
                            "detail": "Token does not exists",
                            "attr": "Token"
                        }
                    ]
                },
                404
            )