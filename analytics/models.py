from django.db import models
from collector.models import Source, Article


class Event(models.Model):
    title = models.CharField(max_length=500)
    articles = models.ManyToManyField(Article, related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)
    risk_score = models.FloatField(default=0.0)
    #метрики кластеризації
    cosine_threshold = models.FloatField(default=0.0)
    article_count_snapshot = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    @property
    def article_count(self):
        return self.articles.count()

    @property
    def sources_count(self):
        return self.articles.values('source').distinct().count()


class CoordinatedGroup(models.Model):
    sources = models.ManyToManyField(Source, related_name='groups')
    detected_at = models.DateTimeField(auto_now_add=True)
    risk_score = models.FloatField(default=0.0)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Група {self.id} (ризик: {self.risk_score:.1f})"


class SimilarityRecord(models.Model):
    source_a = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='similarities_as_a')
    source_b = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='similarities_as_b')

    #метрики кластеризації
    cosine_similarity = models.FloatField(default=0.0)
    euclidean_distance = models.FloatField(default=0.0)
    manhattan_distance = models.FloatField(default=0.0)
    similarity_score = models.FloatField(default=0.0)
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('source_a', 'source_b')

    def __str__(self):
        return f"{self.source_a.name} ↔ {self.source_b.name} (cos: {self.cosine_similarity:.3f})"
    


class SourceNetworkMetrics(models.Model):
    source = models.OneToOneField(Source, on_delete=models.CASCADE, related_name='network_metrics')
    degree_centrality = models.FloatField(default=0.0)
    betweenness_centrality = models.FloatField(default=0.0)
    connections_count = models.IntegerField(default=0)
    calculated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.source.name} (degree: {self.degree_centrality:.3f})"