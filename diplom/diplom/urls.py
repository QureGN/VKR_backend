"""Imagecontainer URL Configuration 
 
 
The urlpatterns list routes URLs to views. For more information please see: 
    https://docs.djangoproject.com/en/4.1/topics/http/urls/ 
Examples: 
Function views 
    1. Add an import:  from my_app import views 
    2. Add a URL to urlpatterns:  path('', views.home, name='home') 
Class-based views 
    1. Add an import:  from other_app.views import Home 
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home') 
Including another URLconf 
    1. Import the include() function: from django.urls import include, path 
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls')) 
""" 
from django.contrib import admin 
from django.urls import path 
import app.views as views 
from django.conf.urls.static import static 
from django.conf import settings 
 
urlpatterns = [ 
    path('admin/', admin.site.urls),
    
    
    path('upload/<str:folder_name>/', views.upload_file),  # POST
    path('listObjectsObj/', views.Obj_from_minio), # GET
    path('download/<str:folder_name>/<str:file_name>/', views.download_file_from_minio), # GET
    path('delete/<str:bucket_name>/<str:file_name>/', views.delete_file), # DELETE
    path('binary/search/<str:folder_name>/', views.search_binary),

    path('trees/review/', views.jsonTrees),
    path('trees/search/<int:folder_id>/', views.search_tree),
    path('trees/<int:tree_id>/', views.get_trees_by_id),  # GET
    path('trees/update/<int:tree_id>/', views.update_tree),  # PUT
    path('trees/delete/<int:tree_id>/', views.delete_tree),  # DELETE
    path('trees/create/', views.create_tree),  # POST

    path('folders/review/', views.folders), # GET
    path('folders/create/', views.create_folder), # post
    path('folders/review/<str:folder_id>/', views.get_folder_by_id),
    path('folders/search/', views.search_folders),  # GET
    # path('folders/<int:folder_id>/<str:folder_name>/', views.get_folder_by_id),  # GET
    path('folders/<str:folder_id>/', views.get_folder_by_idTree),  # GET
    path('folders/binary/<str:folder_name>/', views.get_folder_by_idBin),  # GET
    path('folders/update/<int:folder_id>/<str:folder_name>/', views.update_folder),  # PUT
    path('folders/delete/<int:folder_id>/<str:folder_name>/', views.delete_folder),  # DELETE
    # path('folders/create/', views.folders),  # POST
     
    # path('api/products/search/', views.create_tree),  # GET 
    # path('api/products/search1/', views.jsonTrees), 
    # path('api/products/search2/', views.TreesViewSet), 
]