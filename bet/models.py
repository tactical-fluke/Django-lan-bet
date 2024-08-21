from django.db import models
from django.contrib.auth.models import AbstractUser, User

# Create your models here.

class WagerUser(AbstractUser):
    balance = models.IntegerField(default=2000)

class Wager(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    pot = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class WagerOption(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    wager = models.ForeignKey(Wager, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Bet(models.Model):
    option = models.ForeignKey(WagerOption, on_delete=models.CASCADE)
    user = models.ForeignKey(WagerUser, on_delete=models.CASCADE)
    value = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.__str__()} - {self.option.__str__()} : {self.value.real}"
    
