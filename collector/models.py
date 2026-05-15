from django.db import models

class Source(models.Model):
    CATEGORY_CHOICES = [
        ('state', 'Державні/надійні'),
        ('quality', 'Якісні приватні'),
        ('mass', 'Масові медіа'),
        ('tabloid', 'Таблоїди/проблемні'),
        ('regional', 'Регіональні'),
    ]

    name = models.CharField(max_length=200)
    url = models.URLField(unique=True)
    rss_url = models.URLField(unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='mass')
    is_active = models.BooleanField(default=True)
    reliability_score = models.FloatField(default=50.0)
    is_suspicious = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def category_color(self):
        colors = {
            'state': 'success',
            'quality': 'primary', 
            'mass': 'info',
            'tabloid': 'warning',
            'regional': 'secondary',
        }
        return colors.get(self.category, 'secondary')


class Article(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=500)
    text = models.TextField(blank=True)
    url = models.URLField(unique=True)
    published_at = models.DateTimeField(null=True)
    collected_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    embedding_json = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.source.name}: {self.title[:50]}"