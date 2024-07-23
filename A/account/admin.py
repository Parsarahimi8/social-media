from django.contrib import admin
from .models import Relation,Profile


#class ProfileInline(admin.StackedInline):
 #   model = Profile

admin.site.register(Relation)
admin.site.register(Profile)