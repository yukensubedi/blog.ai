from django.core.management.base import BaseCommand
from assistant.models import Blog
from django.utils import timezone
class Command(BaseCommand):
    help = ' Update status of scheduled blogs to published'

    def handle(self, *args, **options):
        scheduled_blogs = Blog.objects.filter(status = 'scheduled', scheduled_time__lte = timezone.now())

        for blog in scheduled_blogs:
            blog.update_status()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated status for {blog.title}'))
