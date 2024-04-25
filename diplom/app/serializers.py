from rest_framework import serializers

from .models import *


class TreesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trees_json
        fields = ['pk', 'folder_pk','name_tree', 'breed', 'age', 'diameter', 'height', 'coordinate_X', 'coordinate_Y']


class FoldersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folders
        fields = ['pk','name_folder', ]

