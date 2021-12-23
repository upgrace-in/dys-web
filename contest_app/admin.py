from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models
from contest_app.models import users_data

admin.site.register(users_data)