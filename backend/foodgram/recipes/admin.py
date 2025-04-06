from django.contrib import admin

from .models import Recipe, Ingredient


# class PostAdmin(admin.ModelAdmin):
#     list_display = ('pk', 'text', 'pub_date', 'author')
#     search_fields = ('text',)
#     list_filter = ('pub_date',)
#     empty_value_display = '-пусто-'


admin.site.register(Recipe)
admin.site.register(Ingredient)
