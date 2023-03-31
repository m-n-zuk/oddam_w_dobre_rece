from django.contrib.auth.models import User
from django.db import models


TYPES = (
    (1, "fundacja"),
    (2, "organizacja pozarządowa"),
    (3, "zbiórka lokalna")
)


class Category (models.Model):
    name = models.CharField(null=False, max_length=300)

    def __str__(self):
        return self.name


class Institution (models.Model):
    name = models.CharField(null=False, max_length=300)
    description = models.TextField(null=True)
    type = models.IntegerField(choices=TYPES, null=False)
    categories = models.ManyToManyField(Category)

    def __str__(self):
        return self.name


class Donation (models.Model):
    quantity = models.IntegerField(null=False)
    categories = models.ManyToManyField(Category)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    address = models.CharField(max_length=300)
    phone_number = models.IntegerField(null=False)
    city = models.CharField(max_length=25)
    zip_code = models.CharField(max_length=25)
    pick_up_date = models.DateField(null=False)
    pick_up_time = models.TimeField(null=False)
    pick_up_comment = models.TextField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None)
