from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from collector.models import Source, Article
from analytics.models import Event, CoordinatedGroup

from django.db.models import Count


from django.http import JsonResponse
from analytics.models import SimilarityRecord
from django.core.management import call_command


def home(request):

    category_stats = Source.objects.values('category').annotate(total=Count('id'))

    category_data = {
        item['category']: item['total']
        for item in category_stats
    }

    context = {
        'total_articles': Article.objects.count(),
        'total_events': Event.objects.count(),
        'total_groups': CoordinatedGroup.objects.count(),
        'total_sources': Source.objects.filter(is_active=True).count(),

        'recent_articles': Article.objects.select_related('source').order_by('-collected_at')[:10],

        'suspicious_sources': Source.objects.filter(
            is_suspicious=True
        ).order_by('reliability_score')[:5],

        'suspicious_count': Source.objects.filter(
            is_suspicious=True
        ).count(),

        'category_data': category_data,
    }

    return render(request, 'dashboard/home.html', context)


def events(request):
    all_events = Event.objects.prefetch_related('articles__source').order_by('-created_at')
    return render(request, 'dashboard/events.html', {'events': all_events})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    articles = event.articles.select_related('source').order_by('-published_at')
    return render(request, 'dashboard/event_detail.html', {'event': event, 'articles': articles})


def sources(request):
    all_sources = Source.objects.annotate_article_count() if hasattr(Source.objects, 'annotate_article_count') else Source.objects.all()
    from django.db.models import Count
    all_sources = Source.objects.annotate(article_count=Count('articles')).order_by('-article_count')
    return render(request, 'dashboard/sources.html', {'sources': all_sources})


def source_detail(request, pk):
    source = get_object_or_404(Source, pk=pk)
    articles = source.articles.order_by('-published_at')[:20]
    return render(request, 'dashboard/source_detail.html', {'source': source, 'articles': articles})


def groups(request):
    all_groups = CoordinatedGroup.objects.prefetch_related('sources').order_by('-risk_score')
    return render(request, 'dashboard/groups.html', {'groups': all_groups})


@login_required(login_url='/login/')
def admin_panel(request):

    context = {
        'total_articles': Article.objects.count(),

        'processed_count': Article.objects.filter(
            is_processed=True
        ).count(),

        'groups_count': CoordinatedGroup.objects.count(),

        'total_sources': Source.objects.count(),

        'suspicious_sources': Source.objects.filter(
            is_suspicious=True
        ).count(),
    }

    return render(request, 'dashboard/admin_panel.html', context)

@login_required(login_url='/login/')
def admin_sources(request):
    from django.db.models import Count
    sources = Source.objects.annotate(article_count=Count('articles')).order_by('category', 'name')
    return render(request, 'dashboard/admin_sources.html', {'sources': sources})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('admin_panel')
        messages.error(request, 'Невірний логін або пароль')
    return render(request, 'dashboard/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


def graph_data(request):

    records = SimilarityRecord.objects.select_related(
        'source_a',
        'source_b'
    )

    nodes = {}
    links = []

    for rec in records:

        nodes[rec.source_a.id] = {
            'id': rec.source_a.id,
            'name': rec.source_a.name,
            'suspicious': rec.source_a.is_suspicious,
        }

        nodes[rec.source_b.id] = {
            'id': rec.source_b.id,
            'name': rec.source_b.name,
            'suspicious': rec.source_b.is_suspicious,
        }

        links.append({
            'source': rec.source_a.id,
            'target': rec.source_b.id,
            'weight': round(rec.cosine_similarity, 2),
        })

    return JsonResponse({
        'nodes': list(nodes.values()),
        'links': links,
    })


@login_required(login_url='/login/')
def run_collect(request):

    call_command('collect_news')

    messages.success(request, 'Збір новин запущено')

    return redirect('admin_panel')


@login_required(login_url='/login/')
def run_process(request):

    call_command('process_articles')

    messages.success(request, 'NLP обробку запущено')

    return redirect('admin_panel')


@login_required(login_url='/login/')
def run_cluster(request):

    call_command('cluster_articles')

    messages.success(request, 'Кластеризацію виконано')

    return redirect('admin_panel')


@login_required(login_url='/login/')
def run_graph(request):

    call_command('build_graph')

    messages.success(request, 'Графовий аналіз виконано')

    return redirect('admin_panel')