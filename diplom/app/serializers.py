from rest_framework import serializers

from .models import *


class TreesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trees_json
        fields = ['pk', 'folder_pk','name_tree', 'breed', 'age', 'diameter', 'height', 'coordinate_X', 'coordinate_Y']


class FoldersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folders
        fields = ['pk','name_folder', 'owner', 'shared']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = User
        # Поля, которые мы сериализуем
        fields = ["pk", "username", "password", "email"]

    

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

class ShareSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)