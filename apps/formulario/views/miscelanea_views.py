from apps.proforestform.models.proforestform import ProforestForm, Period

from ..serializers.proforestform_serializer import ProforestFormSerializer, PeriodSerializer

from rest_framework import status
from rest_framework import generics
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

@permission_classes([IsAuthenticated])
class ProforestFormList(generics.ListAPIView):
    serializer_class = ProforestFormSerializer
    queryset = ProforestForm.objects.all()
   
@permission_classes([IsAuthenticated])
class ProforestPeriodList(generics.ListAPIView):
    serializer_class = PeriodSerializer
    queryset = Period.objects.all()
   