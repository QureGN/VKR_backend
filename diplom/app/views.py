from django.shortcuts import render 
from app.models import * 
from rest_framework import viewsets 
from app.serializers import TreesSerializer, FoldersSerializer, UserSerializer, UserLoginSerializer, ShareSerializer
from rest_framework.decorators import api_view 
from rest_framework.response import Response 
from minio import Minio 
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from minio.error import S3Error
from rest_framework import status
from datetime import datetime
from rest_framework.renderers import JSONRenderer
from translate import Translator
import logging
from minio.api import CopySource
from django.contrib.auth import authenticate
from datetime import *

import jwt
from .jwt_helper import *

@api_view(["GET"]) 
def jsonTrees(request): 
   
    trees = Trees_json.objects.all().order_by('pk') 
    serializer = TreesSerializer(trees, many=True)
    return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST) 
 

@api_view(["GET"])
def get_trees_by_id(request, tree_id):
    token = request.META.get('HTTP_AUTHORIZATION')
    if (check(token)) :
        try:
            tree = Trees_json.objects.get(pk=tree_id)
            serializer = TreesSerializer(tree, many=False)
            return Response(serializer.data)
        except Trees_json.DoesNotExist:
            return JsonResponse({'message': 'Tree does not exist'})
    return Response({'error': 'token end'}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(["POST"])
def create_tree(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    if (check(token)) :
        serializer = TreesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

        return Response(serializer.data
                    , status=status.HTTP_201_CREATED)
    return Response({'error': 'token end'}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    # name_tree = request.POST.get('name_tree')
    # breed = request.POST.get('breed')
    # age = request.POST.get('age')
    # diameter = request.POST.get('diameter')
    # height = request.POST.get('height')
    # coordinate_X = request.POST.get('coordinate_X')
    # coordinate_Y = request.POST.get('coordinate_Y')

    # tree = Trees_json.objects.create(name_tree=name_tree, breed=breed, age=age, diameter=diameter, height=height, coordinate_X=coordinate_X, coordinate_Y=coordinate_Y)

    # return JsonResponse({'message': "tree create"})


@api_view(["DELETE"])
def delete_tree(request, tree_id):
    token = request.META.get('HTTP_AUTHORIZATION')
    if (check(token)) :
        if not Trees_json.objects.filter(pk=tree_id).exists():
            return JsonResponse({'message': 'Tree does not exist'})

        item = Trees_json.objects.get(pk=tree_id)
        item.delete()
        return JsonResponse({'message': 'Tree deleted successfully'})
    return Response({'error': 'token end'}, status=status.HTTP_400_BAD_REQUEST)

    
    
@api_view(["PUT"])
def update_tree(request, tree_id):
    token = request.META.get('HTTP_AUTHORIZATION')
    if (check(token)) :
        if not Trees_json.objects.filter(pk=tree_id).exists():
            return JsonResponse({'message': 'Tree does not exist'})
        tree = Trees_json.objects.get(pk=tree_id)
        serializer = TreesSerializer(tree, data=request.data, many=False, partial=True)

        if serializer.is_valid():
            serializer.save()

        tree.save()

        return Response(serializer.data)
    return Response({'error': 'token end'}, status=status.HTTP_400_BAD_REQUEST)

    


# методы для участков
@api_view(["GET"]) 
def folders(request): 
    token = request.META.get('HTTP_AUTHORIZATION')
    if (check(token)) :
        payload = get_jwt_payload(token)
        
        shared_folder = Folders.objects.filter(shared=payload["user_id"]) 
        owner_folder = Folders.objects.filter(owner=payload["user_id"])
        allfolders = shared_folder | owner_folder
        serializer = FoldersSerializer(allfolders, many=True)
        return Response(serializer.data)
    return Response({'error': 'token end'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(["GET"]) 
def search_folders(request): 
    token = request.META.get('HTTP_AUTHORIZATION')
    if (check(token)) :
        query = request.GET.get("query", "")
        applications = Folders.objects.filter(name_folder__icontains=query)
        serializer = FoldersSerializer(applications, many=True)
        return Response(serializer.data)
    return Response({'error': 'token end'}, status=status.HTTP_400_BAD_REQUEST) 
   

@api_view(["POST"])
def create_folder(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    if (check(token)) :
        serializer = FoldersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            client = Minio(endpoint="localhost:9000", access_key="minio", secret_key="minio124", secure=False)
            client.make_bucket(serializer.data["name_folder"])
            return Response(serializer.data
                            , status=status.HTTP_201_CREATED)
        return Response(serializer.error
                            , status=status.HTTP_400_BAD_REQUEST)
    return Response({'error': "token end"}, status=status.HTTP_400_BAD_REQUEST)    


@api_view(["PUT"])
def share_folder(request, folder_id):
    token = request.META.get('HTTP_AUTHORIZATION')
    if (check(token)) :
        try:
            folder = Folders.objects.get(pk=folder_id)
        except Folders.DoesNotExist:
            return Response({'error': 'Папка не найдена'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FoldersSerializer(folder)
        email = ShareSerializer(data=request.data)
        if email.is_valid():
            try:
                user = User.objects.get(email=email.data["email"])
            except User.DoesNotExist:
                return Response({'error': "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
            
            # Добавление пользователя в поле shared
            folder.shared.add(user)
            folder.save()
            
            return Response(serializer.data)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
    return Response({'error': 'token end'},  status=status.HTTP_400_BAD_REQUEST)  
    

@api_view(["DELETE"])
def delete_folder(request, folder_id, folder_name):
    token = request.META.get('HTTP_AUTHORIZATION')
    if (check(token)) :
        if not Folders.objects.filter(pk=folder_id).exists():
            return JsonResponse({'message': 'Folder does not exist'})
        try:
            item = Folders.objects.get(pk=folder_id)
            item.delete()

            client = Minio(endpoint="localhost:9000", access_key="minio", secret_key="minio124", secure=False)
            client.remove_bucket(folder_name)

            return JsonResponse({'message': 'Folder deleted successfully'})
        except S3Error as err:
            return JsonResponse({'error': str(err)}, status=500)
    return Response({'error': 'token end'}, status=status.HTTP_400_BAD_REQUEST) 

 
    
@api_view(["PUT"])
def update_folder(request, folder_id, folder_name):
    token = request.META.get('HTTP_AUTHORIZATION')
    if (check(token)) :
        client = Minio(endpoint="localhost:9000", access_key="minio", secret_key="minio124", secure=False)
        if not (Folders.objects.filter(pk=folder_id).exists()) and(client.bucket_exists(folder_name)):
            return JsonResponse({'message': 'Folder does not exist'})
    
        try:
            folder = Folders.objects.get(pk=folder_id)
            serializer = FoldersSerializer(folder, data=request.data, many=False, partial=True)

            if serializer.is_valid():
                serializer.save()

            folder.save()

            client.make_bucket(request.data["name_folder"])
        
            # Копируем объекты из старого бакета в новый
            for obj in client.list_objects(folder_name, recursive=True):
                new_object_name = obj.object_name.replace(folder_name, request.data["name_folder"])
                client.copy_object(request.data["name_folder"], new_object_name, f"{folder_name}/{obj.object_name}")
            
            # Удаляем объекты из старого бакета
            for obj in client.list_objects(folder_name, recursive=True):
                client.remove_object(folder_name, obj.object_name)
            
            # Удаляем старый бакет (если он пуст)
            client.remove_bucket(folder_name)

            return Response(serializer.data)
        except S3Error as err:
            return JsonResponse({'error': str(err)}, status=500)
    return Response({'error': 'token end'}, status=status.HTTP_400_BAD_REQUEST)  

  

@api_view(["GET"])
@csrf_exempt 
def get_folder_by_id(request, folder_id):
    token = request.META.get('HTTP_AUTHORIZATION')
    if (check(token)) :
        folder = Folders.objects.get(pk=folder_id)
        serializer = FoldersSerializer(folder, many=False)

        return Response(serializer.data) 
    return Response({'error': 'token end'}, status=status.HTTP_400_BAD_REQUEST) 

    
@api_view(["GET"])
@csrf_exempt 
def get_folder_by_idBin(request, folder_name):
    token = request.META.get('HTTP_AUTHORIZATION')
    if (check(token)) :
        client = Minio(endpoint="localhost:9000", access_key="minio", secret_key="minio124", secure=False)
        bucket_name = folder_name
        # Получение списка объектов (файлов) из бакета MinIO
        objects = client.list_objects(bucket_name, recursive=True)

        file_list = []
        for obj in objects:
            file_info = {
                'name': obj.object_name,
                'size': obj.size,
                'last': obj.last_modified
            }
            file_list.append(file_info)
        
        return Response(file_list)
    return Response({'error': 'token end'}, status=status.HTTP_400_BAD_REQUEST) 

    
@api_view(["GET"])
@csrf_exempt 
def get_files(request, folder_id, folder_name, ):
    token = request.META.get('HTTP_AUTHORIZATION')
    if (check(token)) :
        client = Minio(endpoint="localhost:9000", access_key="minio", secret_key="minio124", secure=False)
        bucket_name = folder_name
        # Получение списка объектов (файлов) из бакета MinIO
        objects = client.list_objects(bucket_name, recursive=True)

        file_list = []
        for obj in objects:
            file_info = {
                'name': obj.object_name,
                'size': obj.size,
                'last': obj.last_modified
            }
            file_list.append(file_info)
        trees = Trees_json.objects.filter(folder_pk = folder_id) 
        serializer = TreesSerializer(trees, many=True)
        return Response({'binary': file_list, 'trees': serializer.data}, status = 200)
    return Response({'error': 'token end'}, status=status.HTTP_400_BAD_REQUEST) 

       

@api_view(["GET"])
@csrf_exempt 
def get_folder_by_idTree(request, folder_id, ):

    token = request.META.get('HTTP_AUTHORIZATION')
    if (check(token)) :
        trees = Trees_json.objects.filter(folder_pk = folder_id) 
        serializer = TreesSerializer(trees, many=True)
        return Response(serializer.data) 
    return Response({'error': 'token end'}, status=status.HTTP_400_BAD_REQUEST) 
    
 
    
@api_view(["GET"])
def search_tree(request, folder_id):
    token = request.META.get('HTTP_AUTHORIZATION')
    if (check(token)) :
        query = request.GET.get("query", "")
        applications = Trees_json.objects.filter(name_tree__icontains=query, folder_pk = folder_id)
        serializer = TreesSerializer(applications, many=True)
        return Response(serializer.data)
    return Response({'error': 'token end'}, status=status.HTTP_400_BAD_REQUEST) 
    

@api_view(["GET"])
def search_binary(request, folder_name):
    token = request.META.get('HTTP_AUTHORIZATION')
    if (check(token)) :
        query = request.GET.get("query", "")
        client = Minio(endpoint="localhost:9000", access_key="minio", secret_key="minio124", secure=False)
        bucket_name = folder_name
        # Получение списка объектов (файлов) из бакета MinIO
        objects = client.list_objects(bucket_name, recursive=True)

        file_list = []
        for obj in objects:
            file_info = {
                'name': obj.object_name,
                'size': obj.size,
                'last': obj.last_modified
            }
            file_list.append(file_info)
        if query:
            filtered_files = [file for file in file_list if file['name'].lower().startswith(query.lower())]
        else:
            filtered_files = file_list
        return Response(filtered_files)
    return Response({'error': 'token end'}, status=status.HTTP_400_BAD_REQUEST) 

    
    
  

@csrf_exempt     
def upload_file(request, folder_name): 
    token = request.META.get('HTTP_AUTHORIZATION')
    if (check(token)) :
        if request.method == 'POST':
            file = request.FILES.get('file')
            
            # Сохраните файл на диск
            
            # Инициализация клиента MinIO
            client = Minio(endpoint="localhost:9000", access_key="minio", secret_key="minio124", secure=False)

            try:

                client.bucket_exists(folder_name)
            except Exception as e:
                
                client.make_bucket(folder_name)
                print(f'Bucket {folder_name} created.')
            file_path = file.name
        
            # Загрузка файла в MinIO
            try:
                client.put_object(folder_name, file_path, file, file.size)
                file_info = {
                    'name': file.name,
                    'size': file.size,
                    'last': datetime.now().isoformat()
                }
                
                return JsonResponse({'files': file_info})

                # return JsonResponse({'message': 'File uploaded to MinIO successfully'})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'File not found in the request'}, status=400)
    return Response({'error': 'token end'}, status=status.HTTP_400_BAD_REQUEST)

    

@csrf_exempt  
def delete_file(request, bucket_name, file_name):
    token = request.META.get('HTTP_AUTHORIZATION')
    if (check(token)) :
        try:
            client = Minio(endpoint="localhost:9000", access_key="minio", secret_key="minio124", secure=False)

            client.remove_object(bucket_name, file_name)
            return JsonResponse({'message': 'File delete'},  status=200)
        except Exception as e:
            return JsonResponse({'message': str(e)},  status=404)
    return Response({'error': 'token end'},  status=400) 

    


@csrf_exempt
@api_view(['PUT'])
def update_file(request, bucket_name, old_file_name):

    token = request.META.get('HTTP_AUTHORIZATION')
    if (check(token)) :
        client = Minio(endpoint="localhost:9000", access_key="minio", secret_key="minio124", secure=False)
    
        try:
            new_file_name = request.data.get('file_name')
            
            # Копирование файла с новым именем
            client.copy_object(
            bucket_name,
            new_file_name,
            CopySource(bucket_name, old_file_name)
            )
            
            # Удаление старого файла
            client.remove_object(bucket_name, old_file_name)
            
            return Response({new_file_name})
        
        except S3Error as err:
            return Response({'error': str(err)}, status=500)
        
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    return Response({'error': 'token end'}, status=status.HTTP_400_BAD_REQUEST) 
    

@csrf_exempt   
def download_file_from_minio(request,folder_name, file_name):

    token = request.META.get('HTTP_AUTHORIZATION')
    if (check(token)) :
        client = Minio(endpoint="localhost:9000",
                   access_key="minio",
                   secret_key="minio124",
                   secure=False)  # Установите на True, если используете HTTPS

        bucket_name = folder_name

        try:
            # Получение объекта (файла) из бакета MinIO
            response = client.get_object(bucket_name, file_name)

            # Установка заголовков для скачивания файла
            response_headers = {
                'Content-Disposition': f'attachment; filename="{file_name}"',
                'Content-Type': 'application/octet-stream',
            }
            # Формирование HTTP-ответа с содержимым файла для скачивания
            response_data = response.read()
            response.close()

            # # Сохранение файла на локальное устройство
            # with open(file_name, 'wb') as file:
            #     file.write(response_data)

            return HttpResponse(response_data, headers=response_headers)
        
            # Формирование HTTP-ответа с содержимым файла
            
        except S3Error as err:
            return HttpResponse(f'Error downloading file: {str(err)}', status=500)
    return Response({'error': 'token end'}, status=status.HTTP_400_BAD_REQUEST) 
    # Инициализация клиента MinIO
    

@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)
    
    user = authenticate(request, username=serializer.data["email"], password=serializer.data["password"])
    
    if user is None:
        return Response({'error': 'Неправильный логин или пароль'}, status=status.HTTP_401_UNAUTHORIZED)
    
    access_token = create_access_token(user.id)
    
    user_data = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'access_token': access_token
    }
    
    return Response(user_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def register(request):
    serializer = UserSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
    user = User.objects.create_user(username=serializer.data["username"], password=serializer.data["password"], email=serializer.data["email"], )
    

    access_token = create_access_token(user.id)

    message = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        "access_token": access_token
    }

    response = Response(message, status=status.HTTP_201_CREATED)
    return response


def check(token):

    try:
        payload = jwt.decode(token, settings.JWT["SIGNING_KEY"], algorithms=['HS256'])
        # Проверка срока действия токена
        expiration_time = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
        
        if expiration_time < datetime.now(tz=timezone.utc):
            return False
        # Проверка в черном списке токенов
        return True
    except jwt.exceptions.InvalidTokenError:
        return False



