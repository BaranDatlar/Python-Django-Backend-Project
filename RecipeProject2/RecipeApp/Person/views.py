from django.shortcuts import render
from .models import user_collection, recipe_collection
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from .serializers import RecipeSerializer, UserSerializer
from bson.objectid import ObjectId
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta, datetime
import RecipeApp.settings as settings
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import uuid



def index(request):
    return HttpResponse("App çalışıyor")


def GetAllUser(request):
    persons = user_collection.find()
    return HttpResponse(persons)

class AddRecipe(APIView):

    def post(self, request, format=None):
        serializer = RecipeSerializer(data=request.data)

        if serializer.is_valid():
            recipe_data = serializer.validated_data
            username = request.user.username
            recipe_data['recipe_owner'] = username
            result = recipe_collection.insert_one(recipe_data)
            recipe_id = result.inserted_id

            user_collection.update_one(
                {"username": username},
                {"$addToSet": {"own_recipes": str(recipe_id)}}
            )
         
            recipe_data['_id'] = str(recipe_id)
            return Response(recipe_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     
class GetAllRecipes(APIView):
    
    def get(self, request, format=None):
        recipes = recipe_collection.find()  
        serializer = RecipeSerializer(recipes, many=True) 
        return Response(serializer.data)
    
class GetRecipeById(APIView):
     
    def post(self, request, format=None):
        # Kullanıcıdan gelen ID'yi al
        recipe_id = request.data.get('id')
        if not recipe_id:
            return Response({"error": "ID parametresi eksik"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            recipe = recipe_collection.find_one({'_id': ObjectId(recipe_id)})
            if recipe:
                serializer = RecipeSerializer(recipe)
                return Response(serializer.data)
            else:
                return Response({"error": "Yemek bulunamadı"}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({"error": "Geçersiz ID veya diğer bir hata"}, status=status.HTTP_400_BAD_REQUEST)
        

class UpdateRecipe(APIView):

    def put(self, request, format=None):
        recipe_id = request.data.get('id')
        recipe_data = request.data.get('data')
        if not recipe_id or not recipe_data:
            return Response({"error": "ID ve güncellenecek veriler gerekli"}, status=status.HTTP_400_BAD_REQUEST)

        try: 
            result = recipe_collection.update_one(
                {'_id': ObjectId(recipe_id)},
                {'$set': recipe_data}
            )
            if result.matched_count == 1:
                updated_recipe = recipe_collection.find_one({'_id': ObjectId(recipe_id)})
                serializer = RecipeSerializer(updated_recipe)
                return Response(serializer.data)
            else:
                return Response({"error": "Yemek bulunamadı"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DeleteRecipe(APIView):

    def post(self, request, format=None):
        recipe_id = request.data.get('id')
        if not recipe_id:
            return Response({"error": "ID parametresi eksik"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = recipe_collection.delete_one({'_id': ObjectId(recipe_id)})
            if result.deleted_count == 1:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "Yemek bulunamadı veya zaten silinmiş"}, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class SearchRecipes(APIView):

    def post(self, request, format=None):
        title = request.data.get('title', '')
        recipes = recipe_collection.find({"title": {"$regex": title, "$options": "i"}})
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data)
    
class AddToFavorites(APIView):
  
    def post(self, request, format=None):
        username = request.user.username  
        recipe_id = request.data.get('id')

        if not recipe_id:
            return Response({"error": "Tarif ID'si gerekli"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = recipe_collection.update_one(
                {'_id': ObjectId(recipe_id)},
                {'$addToSet': {'isFav': str(request.user.username)}}
            )
            if result.matched_count == 1:
                user_collection.update_one(
                    {'username': username},
                    {'$addToSet': {'favorite_recipes': str(recipe_id)}}
                )
                return Response({"message": "Tarif favorilere eklendi"})
            else:
                return Response({"error": "Tarif bulunamadı"}, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class RemoveFromFavorites(APIView):

    def post(self, request, format=None):
        username = request.user.username    
        recipe_id = request.data.get('id')

        if not recipe_id:
            return Response({"error": "Tarif ID'si gerekli"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            result = recipe_collection.update_one(
                {'_id': ObjectId(recipe_id)},
                {'$pull': {'isFav': str(username)}}
            )
            if result.matched_count == 1:
                user_collection.update_one(
                    {'username': username},
                    {'$pull': {'favorite_recipes': str(recipe_id)}}
                )
                return Response({"message": "Tarif favorilerden silindi"})
            else:
                return Response({"error": "Tarif bulunamadı"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class SimpleUser:
    def __init__(self, id, username):
        self.id = id
        self.username = username

        
class UserCreate(APIView):

    permission_classes = [AllowAny]
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user_data = serializer.validated_data
            hashed_password = make_password(user_data['password'])

            inserted_user = user_collection.insert_one({
                "username": user_data['username'],
                "password": hashed_password
            })
            user_id = str(inserted_user.inserted_id)

            django_user, created = User.objects.get_or_create(username=user_data['username'])
            simple_user = SimpleUser(id=user_id, username=django_user.username)

            refresh = RefreshToken.for_user(simple_user)
            access_token = str(refresh.access_token)

            return Response({
                "username": user_data['username'],
                "refresh": str(refresh),
                "access": access_token,
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class UserLogin(APIView):

    permission_classes = [AllowAny]
    def post(self, request, format=None):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Kullanıcı adı ve şifre gerekli"}, status=status.HTTP_400_BAD_REQUEST)

        user_document = user_collection.find_one({"username": username})

        if user_document:
            
            if check_password(password, user_document.get('password')):
                django_user, created = User.objects.get_or_create(username=username)
                simple_user = SimpleUser(id=django_user.id, username=django_user.username)

                refresh = RefreshToken.for_user(simple_user)
                access_token = str(refresh.access_token)

                return Response({
                    "message": "Başarılı giriş",
                    "username": username,
                    "refresh": str(refresh),
                    "access": access_token,
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Geçersiz şifre"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"error": "Kullanıcı bulunamadı"}, status=status.HTTP_404_NOT_FOUND)
    
class GetUserRecipes(APIView):

    def get(self, request, format=None):
        username = request.user.username  
        user = user_collection.find_one({"username": username})
        if user:
            return Response({
                "username": username,
                "recipes": user.get("recipes", [])
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Kullanıcı bulunamadı"}, status=status.HTTP_404_NOT_FOUND)

class GetUserFavorites(APIView):

    def get(self, request, format=None):
        username = request.user.username  
        user = user_collection.find_one({"username": username})
        if user:
            return Response({
                "username": username,
                "Favorite Recipes": user.get("favorite_recipes", [])
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Kullanıcı bulunamadı"}, status=status.HTTP_404_NOT_FOUND)
        
class AddCommentToRecipe(APIView):

    def post(self, request, format=None):
        recipe_id = request.data.get('recipe_id')
        comment_text = request.data.get('comment')
        if not recipe_id or not comment_text:
            return Response({"error": "Tarif ID'si ve yorum gerekli"}, status=status.HTTP_400_BAD_REQUEST)

        username = request.user.username
        comment_id = str(uuid.uuid4())  

        try:   
            result = recipe_collection.update_one(
                {'_id': ObjectId(recipe_id)},
                {'$push': {'comments': {'id': comment_id, 'username': username, 'comment': comment_text}}}
            )
            if result.modified_count == 1:
                return Response({"message": "Yorum başarıyla eklendi", "comment_id": comment_id})
            else:
                return Response({"error": "Tarif bulunamadı"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class DeleteComment(APIView):
   
    def post(self, request, format=None):
        recipe_id = request.data.get('recipe_id')
        comment_id = request.data.get('comment_id')
        if not recipe_id or not comment_id:
            return Response({"error": "Tarif ID'si ve yorum ID'si gerekli"}, status=status.HTTP_400_BAD_REQUEST)

        username = request.user.username

        try:
            result = recipe_collection.update_one(
                {'_id': ObjectId(recipe_id)},
                {'$pull': {'comments': {'id': comment_id, 'username': username}}}
            )
            if result.modified_count == 1:
                return Response({"message": "Yorum başarıyla silindi"})
            else:
                return Response({"error": "Yorum veya tarif bulunamadı"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)