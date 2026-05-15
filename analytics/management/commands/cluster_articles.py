from django.core.management.base import BaseCommand
from collector.models import Article, Source
from analytics.models import Event, CoordinatedGroup, SimilarityRecord
from processor.nlp import cosine_similarity
import json
import numpy as np
from datetime import timedelta


class Command(BaseCommand):
    help = 'Кластеризує статті в події та знаходить скоординовані групи'

    def handle(self, *args, **kwargs):
        self.stdout.write('Завантажуємо векторизовані статті...')

        articles = list(Article.objects.filter(
            is_processed=True
        ).exclude(embedding_json='').select_related('source'))

        self.stdout.write(f'Знайдено {len(articles)} статей з векторами')

        if len(articles) < 2:
            self.stdout.write('Недостатньо статей для аналізу')
            return

        #завантажуємо вектори
        vectors = []
        valid_articles = []
        for article in articles:
            try:
                vec = json.loads(article.embedding_json)
                vectors.append(vec)
                valid_articles.append(article)
            except Exception:
                continue

        self.stdout.write(f'Завантажено {len(vectors)} векторів')
        self.stdout.write('Обчислюємо схожість між статтями...')

        #знаходимо схожі пари статей
        similar_pairs = []
        n = len(vectors)
        for i in range(n):
            for j in range(i + 1, n):
                sim = cosine_similarity(vectors[i], vectors[j])
                if sim > 0.75:
                    similar_pairs.append((i, j, sim))

        self.stdout.write(f'Знайдено {len(similar_pairs)} схожих пар')

        #групуємо в події
        Event.objects.all().delete()

        visited = set()
        events_created = 0

        for i, j, sim in similar_pairs:
            art_i = valid_articles[i]
            art_j = valid_articles[j]

            #перевіряємо часову близькість (24 години)
            if art_i.published_at and art_j.published_at:
                time_diff = abs((art_i.published_at - art_j.published_at).total_seconds())
                if time_diff > 86400:
                    continue

            # створюємо подію
            key = tuple(sorted([art_i.id, art_j.id]))
            if key in visited:
                continue
            visited.add(key)

            #шукаємо чи є вже подія з однією з цих статей
            existing_event = None
            for event in Event.objects.filter(articles=art_i):
                existing_event = event
                break
            for event in Event.objects.filter(articles=art_j):
                existing_event = event
                break

            if existing_event:
                existing_event.articles.add(art_i, art_j)
                existing_event.risk_score = min(1.0, existing_event.risk_score + 0.1)
                existing_event.save()
            else:
                title = art_i.title[:100] if art_i.title else 'Подія'
                event = Event.objects.create(
                    title=title,
                    risk_score=sim
                )
                event.articles.add(art_i, art_j)
                events_created += 1

        self.stdout.write(f'Створено {events_created} подій')

        #знаходимо скоординовані групи джерел
        self.stdout.write('Аналізуємо координацію між джерелами...')

        CoordinatedGroup.objects.all().delete()
        SimilarityRecord.objects.all().delete()

        source_pairs = {}
        for i, j, sim in similar_pairs:
            src_i = valid_articles[i].source
            src_j = valid_articles[j].source
            if src_i.id == src_j.id:
                continue
            key = tuple(sorted([src_i.id, src_j.id]))
            if key not in source_pairs:
                source_pairs[key] = []
            source_pairs[key].append(sim)

        #зберігаємо similarity records з усіма трьома метриками
        groups_created = 0
        for (src_id_a, src_id_b), sims in source_pairs.items():
            avg_sim = sum(sims) / len(sims)
            src_a = Source.objects.get(id=src_id_a)
            src_b = Source.objects.get(id=src_id_b)

            #середні вектори по кожному джерелу для евклідової та манхеттенської
            vecs_a = [vectors[i] for i, art in enumerate(valid_articles) if art.source_id == src_id_a]
            vecs_b = [vectors[j] for j, art in enumerate(valid_articles) if art.source_id == src_id_b]
            mean_a = np.mean(vecs_a, axis=0)
            mean_b = np.mean(vecs_b, axis=0)

            euclidean = float(np.linalg.norm(mean_a - mean_b))
            manhattan = float(np.sum(np.abs(mean_a - mean_b)))

            SimilarityRecord.objects.create(
                source_a=src_a,
                source_b=src_b,
                similarity_score=avg_sim,
                cosine_similarity=avg_sim,
                euclidean_distance=euclidean,
                manhattan_distance=manhattan,
            )

            #висока схожістьі багато спільних статей це скоординована група
            if avg_sim > 0.80 and len(sims) >= 2:
                group = CoordinatedGroup.objects.create(
                    risk_score=avg_sim,
                    description=f'Схожість {avg_sim:.2f}, спільних статей: {len(sims)}'
                )
                group.sources.add(src_a, src_b)

                #позначаємо джерела як підозрілі
                src_a.is_suspicious = True
                src_a.save()
                src_b.is_suspicious = True
                src_b.save()
                groups_created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Готово! Подій: {events_created}, скоординованих груп: {groups_created}'
        ))