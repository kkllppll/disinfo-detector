from django.core.management.base import BaseCommand
from collector.models import Source

class Command(BaseCommand):
    help = 'Завантажує початкові RSS джерела'

    def handle(self, *args, **kwargs):
        sources = [
            #державні надійні
            {
                'name': 'Укрінформ',
                'url': 'https://ukrinform.ua',
                'rss_url': 'https://www.ukrinform.ua/rss/feed.rss',
                'category': 'state',
                'reliability_score': 90.0,
            },
            {
                'name': 'Суспільне',
                'url': 'https://suspilne.media',
                'rss_url': 'https://suspilne.media/rss/all.rss',
                'category': 'state',
                'reliability_score': 88.0,
            },
            {
                'name': 'Радіо Свобода',
                'url': 'https://www.radiosvoboda.org',
                'rss_url': 'https://www.radiosvoboda.org/api/zrqiteuukg',
                'category': 'state',
                'reliability_score': 87.0,
            },
            {
                'name': 'Українська правда',
                'url': 'https://www.pravda.com.ua',
                'rss_url': 'https://www.pravda.com.ua/rss/view_news/',
                'category': 'state',
                'reliability_score': 85.0,
            },
            #якісні приватні
            {
                'name': 'Hromadske',
                'url': 'https://hromadske.ua',
                'rss_url': 'https://hromadske.ua/rss',
                'category': 'quality',
                'reliability_score': 83.0,
            },
            {
                'name': 'LB.ua',
                'url': 'https://lb.ua',
                'rss_url': 'https://lb.ua/rss/ukraine.xml',
                'category': 'quality',
                'reliability_score': 82.0,
            },
            {
                'name': 'Дзеркало тижня',
                'url': 'https://zn.ua',
                'rss_url': 'https://zn.ua/rss/all.rss',
                'category': 'quality',
                'reliability_score': 81.0,
            },
            {
                'name': 'Detector Media',
                'url': 'https://detector.media',
                'rss_url': 'https://detector.media/rss/',
                'category': 'quality',
                'reliability_score': 85.0,
            },
            #масові медіа
            {
                'name': 'TSN',
                'url': 'https://tsn.ua',
                'rss_url': 'https://tsn.ua/rss/full.rss',
                'category': 'mass',
                'reliability_score': 65.0,
            },
            {
                'name': 'Новини 24',
                'url': 'https://24tv.ua',
                'rss_url': 'https://24tv.ua/rss/all.xml',
                'category': 'mass',
                'reliability_score': 63.0,
            },
            {
                'name': 'Факти ICTV',
                'url': 'https://fakty.com.ua',
                'rss_url': 'https://fakty.com.ua/rss/all.xml',
                'category': 'mass',
                'reliability_score': 65.0,
            },
            {
                'name': 'Уніан',
                'url': 'https://www.unian.ua',
                'rss_url': 'https://rss.unian.net/site/news_ukr.rss',
                'category': 'mass',
                'reliability_score': 60.0,
            },
            #таблоїди проблемні
            {
                'name': 'Страна.ua',
                'url': 'https://strana.news',
                'rss_url': 'https://strana.news/rss.xml',
                'category': 'tabloid',
                'reliability_score': 25.0,
            },
            {
                'name': 'Обозреватель',
                'url': 'https://obozrevatel.com',
                'rss_url': 'https://obozrevatel.com/rss.xml',
                'category': 'tabloid',
                'reliability_score': 35.0,
            },
            {
                'name': 'Апостроф',
                'url': 'https://apostrophe.ua',
                'rss_url': 'https://apostrophe.ua/rss',
                'category': 'tabloid',
                'reliability_score': 38.0,
            },
            {
                'name': 'Слово і діло',
                'url': 'https://www.slovoidilo.ua',
                'rss_url': 'https://www.slovoidilo.ua/rss.xml',
                'category': 'tabloid',
                'reliability_score': 40.0,
            },
            #регіональні
            {
                'name': 'Думська (Одеса)',
                'url': 'https://dumskaya.net',
                'rss_url': 'https://dumskaya.net/rss/',
                'category': 'regional',
                'reliability_score': 60.0,
            },
            {
                'name': 'Збруч',
                'url': 'https://zbruc.eu',
                'rss_url': 'https://zbruc.eu/rss.xml',
                'category': 'regional',
                'reliability_score': 70.0,
            },
            {
                'name': 'Харківські новини',
                'url': 'https://kharkiv.informator.ua',
                'rss_url': 'https://kharkiv.informator.ua/feed/',
                'category': 'regional',
                'reliability_score': 58.0,
            },
            {
                'name': 'Бджола',
                'url': 'https://bджола.ua',
                'rss_url': 'https://bджола.ua/feed/',
                'category': 'regional',
                'reliability_score': 62.0,
            },
        ]

        created = 0
        updated = 0
        for s in sources:
            obj, was_created = Source.objects.update_or_create(
                rss_url=s['rss_url'],
                defaults={
                    'name': s['name'],
                    'url': s['url'],
                    'category': s['category'],
                    'reliability_score': s['reliability_score'],
                }
            )
            if was_created:
                created += 1
                self.stdout.write(f"  ✓ {s['name']} [{s['category']}]")
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(f'\nГотово! Додано: {created}, оновлено: {updated}')
        )