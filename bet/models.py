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
    close_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    def total_value(self):
        return self.pot + sum([option.total_value() for option in self.wageroption_set.all()])
    
    def total_num_bets(self):
        return sum([option.num_bets() for option in self.wageroption_set.all()])

class WagerOption(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=2000, blank=True)
    wager = models.ForeignKey(Wager, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    def total_value(self):
        return sum([bet.value for bet in self.bet_set.all()], 0)
    
    def num_bets(self):
        return len(self.bet_set.all())
    
    def winning_ratio(self):
        if self.total_value() > 0:
            return float(self.wager.total_value()) / float(self.total_value())
        else:
            return float('inf')
    
    def percent_bets(self):
        if self.wager.total_num_bets() > 0:
            return (float(self.num_bets()) / float(self.wager.total_num_bets())) * 100.0
        else:
            return float('inf')

class Bet(models.Model):
    option = models.ForeignKey(WagerOption, on_delete=models.CASCADE)
    wager = models.ForeignKey(Wager, on_delete=models.CASCADE)
    user = models.ForeignKey(WagerUser, on_delete=models.CASCADE)
    value = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.__str__()} - {self.option.__str__()} : {self.value.real}"
    
