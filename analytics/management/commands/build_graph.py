from django.core.management.base import BaseCommand
from analytics.models import SimilarityRecord, SourceNetworkMetrics
import networkx as nx


class Command(BaseCommand):
    help = 'Будує граф джерел та розраховує мережеві метрики'

    def handle(self, *args, **kwargs):
        self.stdout.write('Будуємо граф джерел...')

        records = SimilarityRecord.objects.select_related('source_a', 'source_b').all()

        if not records:
            self.stdout.write('Немає даних схожості. Спочатку запустіть cluster_articles')
            return

        G = nx.Graph()

        for rec in records:
            G.add_node(rec.source_a.id, name=rec.source_a.name)
            G.add_node(rec.source_b.id, name=rec.source_b.name)
            G.add_edge(
                rec.source_a.id,
                rec.source_b.id,
                weight=rec.cosine_similarity
            )

        self.stdout.write(f'Граф: {G.number_of_nodes()} вузлів, {G.number_of_edges()} ребер')

        degree_cent = nx.degree_centrality(G)
        betweenness_cent = nx.betweenness_centrality(G, weight='weight')

        SourceNetworkMetrics.objects.all().delete()

        metrics_list = []
        for node_id in G.nodes():
            metrics_list.append(SourceNetworkMetrics(
                source_id=node_id,
                degree_centrality=round(degree_cent.get(node_id, 0.0), 6),
                betweenness_centrality=round(betweenness_cent.get(node_id, 0.0), 6),
                connections_count=G.degree(node_id),
            ))

        SourceNetworkMetrics.objects.bulk_create(metrics_list)

        self.stdout.write(self.style.SUCCESS(
            f'Готово! Метрики розраховано для {len(metrics_list)} джерел'
        ))

        top = sorted(metrics_list, key=lambda x: x.degree_centrality, reverse=True)[:5]
        self.stdout.write('\nТоп-5 джерел за degree centrality:')
        for m in top:
            self.stdout.write(f'  {m.source_id}: degree={m.degree_centrality:.4f}, betweenness={m.betweenness_centrality:.4f}')