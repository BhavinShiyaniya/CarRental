import json
from django.http import HttpResponse
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import datetime

from channels.layers import get_channel_layer
from django.http import HttpResponse
from asgiref.sync import async_to_sync


def schedule_send_otp(celery_schedule_time:datetime.datetime, to_eamil, task_name):
    '''function for schedule otp email one hour before pickup time'''
    hours_diff = (datetime.timedelta(hours=celery_schedule_time.hour)) - (datetime.timedelta(hours=1))
    hours = int(hours_diff.seconds / 3600)
    # hours_diff_str = str(hours_diff)
    # hours = hours_diff_str[0:2]
    
    schedule, created = CrontabSchedule.objects.get_or_create(hour = hours, minute = celery_schedule_time.minute, day_of_month=celery_schedule_time.day, month_of_year=celery_schedule_time.month)
    print("schedule:::", schedule)
    print("To email::", to_eamil)
    task = PeriodicTask.objects.create(crontab=schedule, name='send_otp_before_pickup_'+task_name, task="car.tasks.send_otp", args=json.dumps(([to_eamil])), one_off=True)
    print("➡ task :", task)
    
    return HttpResponse("Done")


def msgfromoutside(request):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'notification',
        {
            'type':'send.message',
            'message': 'Message from outside consumer'
        }
    )

    return HttpResponse("Message Sent from View to Consumer")

