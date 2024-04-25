from django.shortcuts import render 
from app.models import * 
from rest_framework import viewsets 
from app.serializers import TreesSerializer, FoldersSerializer
from rest_framework.decorators import api_view 
from rest_framework.response import Response 
from minio import Minio 
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from minio.error import S3Error


@api_view(["GET"]) 
def jsonTrees(request): 
    query = request.GET.get("query", "") 
 
    trees = Trees_json.objects.all().order_by('pk') 
    serializer = TreesSerializer(trees, many=True)
    return Response(serializer.data) 
 

@api_view(["GET"])
def get_trees_by_id(request, tree_id):

    try:
        tree = Trees_json.objects.get(pk=tree_id)
        serializer = TreesSerializer(tree, many=False)
        return Response(serializer.data)
    except Trees_json.DoesNotExist:
        return JsonResponse({'message': 'Tree does not exist'})

@api_view(["POST"])
def create_tree(request):
    name_tree = request.POST.get('name_tree')
    breed = request.POST.get('breed')
    age = request.POST.get('age')
    diameter = request.POST.get('diameter')
    height = request.POST.get('height')
    coordinate_X = request.POST.get('coordinate_X')
    coordinate_Y = request.POST.get('coordinate_Y')

    tree = Trees_json.objects.create(name_tree=name_tree, breed=breed, age=age, diameter=diameter, height=height, coordinate_X=coordinate_X, coordinate_Y=coordinate_Y)

    return JsonResponse({'message': "tree create"})


@api_view(["DELETE"])
def delete_tree(request, tree_id):
    if not Trees_json.objects.filter(pk=tree_id).exists():
       return JsonResponse({'message': 'Tree does not exist'})

    item = Trees_json.objects.get(pk=tree_id)
    item.delete()
    return JsonResponse({'message': 'Tree deleted successfully'})
    
@api_view(["PUT"])
def update_tree(request, tree_id):
    if not Trees_json.objects.filter(pk=tree_id).exists():
        return JsonResponse({'message': 'Tree does not exist'})
    tree = Trees_json.objects.get(pk=tree_id)
    serializer = TreesSerializer(tree, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    tree.save()

    return Response(serializer.data)


# методы для участков
@api_view(["GET"]) 
def folders(request): 
    trees = Folders.objects.all().order_by('pk') 
    serializer = FoldersSerializer(trees, many=True)
    return Response(serializer.data) 
 
@api_view(["POST"])
def create_folder(request):
    name_folder = request.POST.get('name_folder')
    
    folder = Folders.objects.create(name_folder=name_folder,)
   
    client = Minio(endpoint="localhost:9000", access_key="minio", secret_key="minio124", secure=False)
    client.make_bucket(name_folder)

    return JsonResponse({'message': "folder create"})


@api_view(["DELETE"])
def delete_folder(request, folder_id, folder_name):
    if not Folders.objects.filter(pk=folder_id).exists():
       return JsonResponse({'message': 'Folder does not exist'})

    item = Folders.objects.get(pk=folder_id)
    item.delete()

    client = Minio(endpoint="localhost:9000", access_key="minio", secret_key="minio124", secure=False)
    client.remove_bucket(folder_name)

    return JsonResponse({'message': 'Folder deleted successfully'})
    
@api_view(["PUT"])
def update_folder(request, folder_id):
    if not Folders.objects.filter(pk=folder_id).exists():
        return JsonResponse({'message': 'Folder does not exist'})
    folder = Folders.objects.get(pk=folder_id)
    serializer = TreesSerializer(folder, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    folder.save()

    return Response(serializer.data)

@api_view(["GET"])
@csrf_exempt 
def get_folder_by_id(request, folder_id, folder_name):
    trees = Trees_json.objects.get(folder_pk=folder_id)
    serializer = TreesSerializer(trees, many=False)

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
    
        return Response({'trees': serializer.data, 'files': file_list})
    
 
@csrf_exempt     
def Obj_from_minio(request):
    client = Minio(endpoint="localhost:9000", access_key="minio", secret_key="minio124", secure=False)
    bucket_name = "obj-files"

    try:
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
        return JsonResponse({'files': file_list})
    
    except S3Error as err:
        return JsonResponse({'error': str(err)}, status=500)
    


@csrf_exempt     
def upload_file(request, folder_name): 
    
    if request.method == 'POST':
        file = request.FILES['file']
        
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
            return JsonResponse({'message': 'File uploaded to MinIO successfully'})
        except Exception as e:
             return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'File not found in the request'}, status=400)

@csrf_exempt  
def delete_file(request, bucket_name, file_name):
    try:
        client = Minio(endpoint="localhost:9000", access_key="minio", secret_key="minio124", secure=False)

        client.remove_object(bucket_name, file_name)
        return JsonResponse({'message': 'File delete'})
    except Exception as e:
        return JsonResponse({'message': str(e)})



@csrf_exempt   
def download_file_from_minio(request,folder_name, file_name):
    # Инициализация клиента MinIO
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