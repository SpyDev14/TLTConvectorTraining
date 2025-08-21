from django.contrib import admin


class BaseRenderableModelAdmin(admin.ModelAdmin):
	prepopulated_fields = {'slug': ['name']}
