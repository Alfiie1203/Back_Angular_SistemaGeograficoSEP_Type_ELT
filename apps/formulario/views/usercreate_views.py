from apps.user.models import User, Role
from django.contrib.auth.models import (Group)
from datetime import datetime
from apps.company.models.company import CompanyUserFormKey

from rest_framework.views import APIView
from rest_framework.response import Response

from apps.user.serializers.user_serializers import CreateUserFormSerializer

class CreateUserKey(APIView):
    permission_classes = []
    serializer_class = CreateUserFormSerializer

    def post(self, request, *args, **kwargs):

        ''' Valida que el email enviado por el usuario sea valido '''
        dataform = dict(request.data)
        slug_key = request.data['key']
        if User.objects.filter(email=dataform['email']).exists():
            key = CompanyUserFormKey.objects.get(slug = slug_key)
            key.delete()
            return Response(
                {
                    "type": "validation_error",
                    "errors": [
                        {
                            "code": "assigned_user",
                            "detail": "The user already exists in the database ",
                            "attr": "User"
                        }
                    ]
                },
                403
            )  

        if CompanyUserFormKey.objects.filter(slug = slug_key).exists():
            key = CompanyUserFormKey.objects.get(slug = slug_key)
            dataform['company'] = key.company.id
            serializer = CreateUserFormSerializer(data=dataform)

            if serializer.is_valid():
                new_user = serializer.save(
                    role = Role.objects.get(name='CLIENTE'),
                    accept_terms_conditions = True,
                    accept_terms_date = datetime.now()  
                )
                group_usuario = Group.objects.get(name='USUARIO')
                group_usuario.user_set.add(new_user)
                key.delete()

                return Response(
                            {
                                "type": "validation_error",
                                "errors": [
                                    {   "code": "error_in_form",
                                        "detail": "This form is incomplete ",
                                        "attr": "new user"
                                    }
                                ] }, 201
                        )
            else:
                return Response( { "type": "bad_request", "errors": serializer.errors }, 400 )
        else:
            return Response(
                        {
                            "type": "validation_error",
                            "errors": [
                                {   "code": "not_exists",
                                    "detail": "This link is Useless ",
                                    "attr": "email"
                                }
                            ] }, 401
                    )
            

        
