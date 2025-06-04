from recipes.models import Recipe, Ingredient, RecipeIngredient
from rest_framework import serializers
from backend.serializers import Base64ImageField
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def to_internal_value(self, data):
        # Обработка входных данных при создании/обновлении
        data = super().to_internal_value(data)
        return {
            'ingredient': data['id'],
            'amount': data['amount']
        }

    def to_representation(self, instance):
        # Форматирование вывода
        representation = super().to_representation(instance)
        if isinstance(instance, RecipeIngredient):
            representation['id'] = instance.ingredient.id
            representation['name'] = instance.ingredient.name
            representation['measurement_unit'] = instance.ingredient.measurement_unit
        return representation


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='ingredient_amounts',
        read_only=False
    )

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'author', 'image',
                  'text', 'ingredients', 'cooking_time', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.favorites.filter(pk=obj.pk).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.shopping_card.filter(pk=obj.pk).exists()
        return False

    def get_author(self, obj):
        from users.serializers import CustomUserViewSerializer
        return CustomUserViewSerializer(obj.author, context=self.context).data

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url)
        return None

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredient_amounts')
        recipe = Recipe.objects.create(**validated_data)
        recipe.image = validated_data.get('image')

        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredient_amounts', None)

        if ingredients_data is not None:
            instance.ingredients.clear()
            for ingredient_data in ingredients_data:
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient_data['ingredient'],
                    amount=ingredient_data['amount']
                )

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance


class ShortRecipeSerializer(RecipeSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
