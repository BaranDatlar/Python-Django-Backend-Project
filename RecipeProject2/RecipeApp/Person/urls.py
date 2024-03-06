from django.urls import path, include
from . import views
from .views import AddRecipe, GetRecipeById, GetAllRecipes, UpdateRecipe, DeleteRecipe, SearchRecipes, AddToFavorites, RemoveFromFavorites, UserCreate, UserLogin, GetUserRecipes, GetUserFavorites, AddCommentToRecipe, DeleteComment


urlpatterns = [
    path('', views.index, name="index"),
    path('GetAllUser/', views.GetAllUser, name="get_all_user"),
    path('AddRecipe/',AddRecipe.as_view(), name="add_recipe"),
    path('GetAllRecipes/',GetAllRecipes.as_view(), name="get_all_recipes"),
    path('GetRecipeById/',GetRecipeById.as_view(), name="get_recipe_by_id"),
    path('UpdateRecipe/',UpdateRecipe.as_view(), name="update_recipe"),
    path('DeleteRecipe/',DeleteRecipe.as_view(), name="delete_recipe"),
    path('SearchRecipe/',SearchRecipes.as_view(), name="search_recipe"),
    path('AddToFavorites/',AddToFavorites.as_view(), name="add_to_favorites"),
    path('RemoveFromFavorites/',RemoveFromFavorites.as_view(), name="remove_from_favorites"),
    path('UserCreate/', UserCreate.as_view(), name='user_create'),
    path('UserLogin/', UserLogin.as_view(), name='user_login'),
    path('GetUserRecipes/', GetUserRecipes.as_view(), name='get_user_recipes'),
    path('GetUserFavorites/', GetUserFavorites.as_view(), name='get_user_favorites'),
    path('AddCommentToRecipe/', AddCommentToRecipe.as_view(), name='get_user_favorites'),
    path('DeleteComment/', DeleteComment.as_view(), name='delete_comment'),
]
