from rest_framework import serializers
from django.contrib.auth.models import Group

class SubroleSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField('get_user_permissions')

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']
    
    def get_user_permissions(self, obj):
        array = []
        for permission in obj.permissions.all():
            array.append(permission.codename)
        return array


class SubroleSerializerBackoffice(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

# class SubroleSerializer(serializers.ModelSerializer):
#     permissions = serializers.SerializerMethodField('get_user_permissions')

#     class Meta:
#         model = Group
#         fields = ['id', 'name', 'permissions']
    
#     def get_user_permissions(self, obj):
#         dict = {}
#         for perm in obj.permissions.all():
#             if perm.content_type.model not in dict:
#                 dict[perm.content_type.model] = [perm.codename]
#             else:
#                 dict[perm.content_type.model].append(perm.codename)
#         return dict