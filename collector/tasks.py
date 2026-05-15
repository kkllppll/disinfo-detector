import feedparser
import trafilatura
from datetime import datetime
from django.utils import timezone
from .models import Source, Article


def fetch_rss(source):
    try:
        feed = feedparser.parse(source.rss_url)
        new_count = 0

        for entry in feed.entries[:20]:
            url = entry.get('link', '')
            if not url:
                continue

            if Article.objects.filter(url=url).exists():
                continue

            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    published_at = timezone.make_aware(
                        datetime(*entry.published_parsed[:6])
                    )
                except Exception:
                    pass

            text = entry.get('summary', '') or ''
            if len(text) < 200:
                try:
                    downloaded = trafilatura.fetch_url(url)
                    if downloaded:
                        full_text = trafilatura.extract(downloaded)
                        if full_text:
                            text = full_text
                except Exception:
                    pass

            Article.objects.create(
                source=source,
                title=entry.get('title', '')[:500],
                text=text,
                url=url,
                published_at=published_at,
            )
            new_count += 1

        return new_count

    except Exception as e:
        print(f"Помилка збору {source.name}: {e}")
        return 0


def collect_all_sources():
    sources = Source.objects.filter(is_active=True)
    total = 0
    for source in sources:
        count = fetch_rss(source)
        total += count
        print(f"{source.name}: +{count} статей")
    print(f"Всього нових статей: {total}")
    return total