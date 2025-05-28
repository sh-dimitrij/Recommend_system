# rec_core/recommender.py
from collections import defaultdict
from django.db.models import Avg, Count
from .models import EBook, ModuleProgress

ALPHA, BETA = 0.6, 0.4          # веса CF- и CB-компонент

def _tag_score(book_tags, user_tags):
    """Совпавшие тэги = 1 балл; можно усложнять."""
    return len(set(book_tags) & set(user_tags))

def _cf_score(user, book_ids):
    """
    Очень лёгкий CF: берём студентов с близкой средней успеваемостью
    и смотрим, какие книги им чаще рекомендуют/отмечают.
    Сейчас — частота книги среди таких студентов.
    """
    user_avg = ModuleProgress.objects.filter(student=user) \
                                     .aggregate(a=Avg('score'))['a'] or 0
    window = 10  # допустим, ±10 баллов
    similar = ModuleProgress.objects \
        .values('student') \
        .annotate(avg=Avg('score')) \
        .filter(avg__gte=user_avg-window, avg__lte=user_avg+window) \
        .values_list('student', flat=True)

    # у вас пока нет таблицы истории рекомендаций —
    # поэтому притворимся, что «популярная книга» = чаще всего встречается у похожих
    pop = (EBook.objects
           .filter(id__in=book_ids)
           .annotate(cnt=Count('id'))
           .values_list('id', 'cnt'))
    return {bid: cnt for bid, cnt in pop}
    

def recommend_for(user, top_k=5):
    """Вернёт список EBook-ов, отсортированный по гибридному скору."""
    # ----- контентная часть --------------------------------------------------
    form = getattr(user, 'questionnaire', None)
    if not form:
        user_tags = []
        lvl = None
    else:
        user_tags = list(form.interest_tags.values_list('id', flat=True))
        lvl       = form.difficulty_level

    # фильтрация книг по сложности, если выбрана
    base_qs = EBook.objects.all()
    if lvl:
        base_qs = base_qs.filter(difficulty_level=lvl)

    # ----- вычисляем очки за тэги -------------------------------------------
    cb_scores = {}
    for book in base_qs.prefetch_related('tags'):
        cb_scores[book.id] = _tag_score(
            list(book.tags.values_list('id', flat=True)), user_tags
        )

    # ----- простая коллаборативная часть ------------------------------------
    cf_scores = _cf_score(user, cb_scores.keys())

    # ----- финальный скор ----------------------------------------------------
    scored = []
    for bid, cb in cb_scores.items():
        cf = cf_scores.get(bid, 0)
        final = ALPHA*cf + BETA*cb
        if final:                   # отбрасываем нули
            scored.append((final, bid))

    scored.sort(reverse=True)
    top_ids = [bid for _, bid in scored[:top_k]]
    # Сохраняем порядок вручную, чтобы QuerySet не перемешал
    books_by_id = {b.id: b for b in base_qs.filter(id__in=top_ids)}
    return [books_by_id[i] for i in top_ids]
