from rest_framework import serializers
from bson.objectid import ObjectId

class RecipeSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    recipe_owner = serializers.CharField(max_length=200,required=False)
    description = serializers.CharField()
    isFav = serializers.ListField(
        child=serializers.CharField(), 
        required=False
    )
    comments = serializers.ListField(
        child=serializers.DictField(),  
        required=False
    )

class UserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True)
    own_recipes = serializers.ListField(
        child=serializers.CharField(), 
        required=False
    )
    favorite_recipes = serializers.ListField(
        child=serializers.CharField(),  
        required=False
    )
    token = serializers.CharField(read_only=True)

    def to_representation(self, instance):    
        ret = super().to_representation(instance)
        ret['recipes'] = [str(recipe_id) for recipe_id in instance.get('recipes', [])]
        return ret

    def to_internal_value(self, data):
        internal = super().to_internal_value(data)
        if 'recipes' in internal:
            internal['recipes'] = [ObjectId(recipe_id) for recipe_id in internal['recipes']]
        return internal
