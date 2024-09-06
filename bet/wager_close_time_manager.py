from .models import Wager
from django.utils import timezone
import threading
from multiprocessing import Manager
from time import sleep

def wager_close_manager(rest_time): 
    print("wager close time manager running")
    while True:
        now = timezone.now()
        for wager in Wager.objects.filter(open=True):
            if wager.close_time is not None and wager.close_time < now:
                print(f"closing wager {wager.name}")
                wager.open = False
                wager.save()
        sleep(rest_time)
        