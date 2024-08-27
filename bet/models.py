from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class WagerUser(AbstractUser):
    balance = models.IntegerField(default=2000)

class Wager(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    pot = models.PositiveIntegerField()
    open = models.BooleanField(default=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    def total_wager_value(self):
        return self.pot + sum(map(WagerOption.option_total_value, self.wageroption_set.all()))

class WagerOption(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    wager = models.ForeignKey(Wager, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    def option_total_value(self):
        return sum(map(lambda bet: bet.value, self.bet_set.all()), 0)

class Bet(models.Model):
    option = models.ForeignKey(WagerOption, on_delete=models.CASCADE)
    wager = models.ForeignKey(Wager, on_delete=models.CASCADE)
    user = models.ForeignKey(WagerUser, on_delete=models.CASCADE)
    value = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.__str__()} - {self.option.__str__()} : {self.value.real}"
    
