from django.db import models
from django.db.models.base import ModelStateFieldsCacheDescriptor
from django.db.models.fields import CharField
from django.utils.translation import TranslatorCommentWarning
import uuid 

class users_data(models.Model):
    id = models.CharField(primary_key=True, max_length=200)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    mail_id = models.CharField(max_length=100)
    phone_num = models.CharField(max_length=100)
    occupation = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    lang = models.CharField(max_length=100)

    razorpay_order_id = models.CharField(max_length=1000, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=1000, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return self.mail_id