from django.core.management.base import BaseCommand
from django.utils import timezone
from clothing.models import ClothingItem

class Command(BaseCommand):
    help = "Check for overdue clothing items and send email alerts"

    def handle(self, *args, **kwargs):
        overdue_items = ClothingItem.objects.filter(availability='checked_out', due_date__lt=timezone.now().date())

        for item in overdue_items:
            item.check_if_overdue()

        self.stdout.write(self.style.SUCCESS(f"Checked {overdue_items.count()} overdue items"))
