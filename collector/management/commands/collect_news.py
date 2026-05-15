from django.core.management.base import BaseCommand
from collector.tasks import collect_all_sources


class Command(BaseCommand):
    help = 'Збирає новини з усіх RSS джерел'

    def handle(self, *args, **kwargs):
        self.stdout.write('Починаємо збір новин...')
        total = collect_all_sources()
        self.stdout.write(
            self.style.SUCCESS(f'Зібрано {total} нових статей!')
        )