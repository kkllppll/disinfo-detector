from django.core.management.base import BaseCommand
from collector.models import Article
from processor.nlp import vectorize_text
import json


class Command(BaseCommand):
    help = 'Векторизує статті через NLP модель'

    def handle(self, *args, **kwargs):
        articles = Article.objects.filter(
            is_processed=False
        ).exclude(text='')[:50]

        if not articles:
            self.stdout.write('Немає статей для обробки')
            return

        self.stdout.write(f'Обробляємо {articles.count()} статей...')

        processed = 0
        for article in articles:
            try:
                content = f"{article.title}. {article.text[:500]}"
                vector = vectorize_text(content)
                if vector:
                    article.embedding_json = json.dumps(vector)
                    article.is_processed = True
                    article.save(update_fields=['embedding_json', 'is_processed'])
                    processed += 1
                    if processed % 10 == 0:
                        self.stdout.write(f'  Оброблено: {processed}')
            except Exception as e:
                self.stdout.write(f'  Помилка {article.id}: {e}')

        self.stdout.write(self.style.SUCCESS(f'Готово! Векторизовано {processed} статей'))
