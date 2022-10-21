from __future__ import unicode_literals
from unicodedata import name

from django.db import models
from django.core.validators import *

from django.contrib.auth.models import User, Group

from django.contrib import admin
import base64

from numpy import size

# Validators for model fields
alphaNumericValidator = RegexValidator(regex='^[a-zA-Z0-9]+$')
alphaNumericSpaceValidator = RegexValidator(regex='^[a-zA-Z0-9 ]+$')
sizeCategoryValidator = RegexValidator(regex='^Tiny|Small|Medium|Large$')
range1to5Validator = [MinValueValidator(1), MaxValueValidator(5)]

# Misc constants
oldestDogEver = 30

class Event(models.Model):
    eventtype = models.CharField(validators=[alphaNumericValidator], max_length=1000, blank=False)
    timestamp = models.DateTimeField()
    userid = models.CharField(max_length=1000, blank=True)
    requestor = models.GenericIPAddressField(blank=False)

    def __str__(self):
        return str(self.eventtype)

    class EventAdmin(admin.ModelAdmin):
        list_display = ('eventtype', 'timestamp')

class ApiKey(models.Model):
    owner = models.CharField(max_length=1000, blank=False)
    key = models.CharField(max_length=5000, blank=False)

    def __str__(self):
        return str(self.owner) + str(self.key)
        
    class ApiKeyAdmin(admin.ModelAdmin):
        list_display = ('owner','key')


class Breed(models.Model):
    name = models.CharField(validators=[alphaNumericValidator], max_length=30, blank=False)
    size = models.CharField(validators=[sizeCategoryValidator], max_length=7, blank=False)
    friendliness = models.IntegerField(validators=range1to5Validator)
    trainability = models.IntegerField(validators=range1to5Validator)
    sheddingammount = models.IntegerField(validators=range1to5Validator)
    exerciseneeds = models.IntegerField(validators=range1to5Validator)

    def __str__(self):
        return self.name

    class BreedAdmin(admin.ModelAdmin):
        list_display = ('name', 'size', 'friendliness', 'trainability', 'sheddingammount', 'exerciseneeds')

class Dog(models.Model):
    name = models.CharField(validators=[alphaNumericValidator], max_length=30, blank=False)
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(oldestDogEver + 1)])
    breed = models.ForeignKey('Breed', on_delete=models.CASCADE, blank=False)
    gender = models.CharField(validators=[alphaNumericValidator], max_length=30)
    color = models.CharField(validators=[alphaNumericValidator], max_length=30)
    favoritefood = models.CharField(validators=[alphaNumericSpaceValidator], max_length=30)
    favoritetoy = models.CharField(validators=[alphaNumericSpaceValidator], max_length=30)

    def __str__(self):
        return "%s (%s)" % self.name, self.breed
    
    class DogAdmin(admin.ModelAdmin):
        list_display = ('name', 'age', 'breed', 'gender', 'color', 'favoritefood', 'favoritetoy')

    