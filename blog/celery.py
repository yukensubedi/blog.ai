import os

from celery import Celery
from celery.schedules import crontab

# celery -A blog beat -l INFO 
# celery -A blog worker -l info -P solo 


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog.settings')

app = Celery('blog')

app.config_from_object('django.conf:settings', namespace='CELERY')


app.conf.broker_connection_retry_on_startup = True


# Celery Beat Settings
app.conf.beat_schedule = {
    'update_scheduled_blogs_task': {
        'task': 'assistant.tasks.update_scheduled_blogs_task',
        'schedule': 30 #runs every 30 secs/ can also use other functions like contrab 
        #'args': (2,)
    }
    
}

app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 