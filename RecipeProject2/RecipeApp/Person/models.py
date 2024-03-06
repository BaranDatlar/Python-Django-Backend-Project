from django.db import models
from db_connect import db
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User


user_collection = db["Users"]
recipe_collection = db["Recipes"]

class MongoDBUserAuthentication(BaseBackend):
    def authenticate(self, request, username=None, **kwargs):
        user_document = user_collection.find_one({"username": username})
        if user_document is not None:
            user = User(username=user_document["username"])
            return user
        return None