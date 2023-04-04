from ..models.proforestform import Period
from ..serializers.period_serializer import PeriodSerializer

from rest_framework import generics
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated



@permission_classes([IsAuthenticated])
class PeriodList(generics.ListAPIView):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer



