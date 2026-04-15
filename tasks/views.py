import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.utils import timezone
from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt
from .models import Task
from .parser import parse_voice_transcript
from datetime import timedelta


@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)
    pending = tasks.filter(status='pending').count()
    completed = tasks.filter(status='completed').count()
    cancelled = tasks.filter(status='cancelled').count()
    delayed = tasks.filter(status='delayed').count()

    # Streak calculation
    streak = _calculate_streak(request.user)
    productivity_score = _productivity_score(request.user)

    context = {
        'tasks': tasks[:20],
        'pending': pending,
        'completed': completed,
        'cancelled': cancelled,
        'delayed': delayed,
        'streak': streak,
        'productivity_score': productivity_score,
        'total': tasks.count(),
    }
    return render(request, 'tasks/dashboard.html', context)


@login_required
def task_list(request):
    status_filter = request.GET.get('status', 'all')
    tasks = Task.objects.filter(user=request.user)
    if status_filter != 'all':
        tasks = tasks.filter(status=status_filter)
    return render(request, 'tasks/task_list.html', {'tasks': tasks, 'status_filter': status_filter})


@login_required
def analytics(request):
    user = request.user
    tasks = Task.objects.filter(user=user)
    now = timezone.now()
    last_30 = now - timedelta(days=30)

    # Build chart data for last 30 days
    daily_data = []
    for i in range(29, -1, -1):
        day = (now - timedelta(days=i)).date()
        day_tasks = tasks.filter(created_at__date=day)
        daily_data.append({
            'date': day.strftime('%b %d'),
            'created': day_tasks.count(),
            'completed': day_tasks.filter(status='completed').count(),
            'delayed': day_tasks.filter(status='delayed').count(),
        })

    # On time vs late completions — computed in Python using model property
    completed_tasks = list(tasks.filter(status='completed', due_date__isnull=False, completed_at__isnull=False))
    on_time_count = sum(1 for t in completed_tasks if t.completed_on_time is True)
    late_count = len(completed_tasks) - on_time_count

    # Best day of week
    from django.db.models.functions import ExtractWeekDay
    best_day_data = (
        tasks.filter(status='completed')
        .annotate(weekday=ExtractWeekDay('completed_at'))
        .values('weekday')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    days_map = {1: 'Sun', 2: 'Mon', 3: 'Tue', 4: 'Wed', 5: 'Thu', 6: 'Fri', 7: 'Sat'}
    best_day_chart = [{'day': days_map.get(d['weekday'], '?'), 'count': d['count']} for d in best_day_data]

    context = {
        'total': tasks.count(),
        'pending': tasks.filter(status='pending').count(),
        'completed': tasks.filter(status='completed').count(),
        'delayed': tasks.filter(status='delayed').count(),
        'cancelled': tasks.filter(status='cancelled').count(),
        'on_time_count': on_time_count,
        'late_count': late_count,
        'daily_data_json': json.dumps(daily_data),
        'best_day_json': json.dumps(best_day_chart),
        'streak': _calculate_streak(user),
        'productivity_score': _productivity_score(user),
        'overdue_count': sum(1 for t in tasks.filter(status='pending') if t.is_overdue),
    }
    return render(request, 'tasks/analytics.html', context)



@login_required
@require_POST
def parse_voice(request):
    """Parse voice transcript via Gemini and return structured data."""
    try:
        data = json.loads(request.body)
        transcript = data.get('transcript', '').strip()
        if not transcript:
            return JsonResponse({'success': False, 'error': 'Empty transcript'}, status=400)

        result = parse_voice_transcript(transcript)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def create_task(request):
    """Create a task from parsed voice data."""
    try:
        data = json.loads(request.body)
        due_date = None
        if data.get('due_date_iso'):
            from django.utils.dateparse import parse_datetime
            due_date = parse_datetime(data['due_date_iso'])

        task = Task.objects.create(
            user=request.user,
            title=data.get('title', 'Untitled Task'),
            description=data.get('description', ''),
            due_date=due_date,
            voice_transcript=data.get('transcript', ''),
            parser_confidence=data.get('confidence', 1.0),
            status='pending',
        )
        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'status': task.status,
                'created_at': task.created_at.isoformat(),
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    try:
        data = json.loads(request.body)
        action = data.get('action')
        if action == 'complete':
            task.mark_completed()
        elif action == 'cancel':
            task.mark_cancelled()
        elif action == 'delay':
            days = int(data.get('days', 1))
            task.delay(days)
        else:
            return JsonResponse({'success': False, 'error': 'Unknown action'}, status=400)

        return JsonResponse({'success': True, 'status': task.status})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def get_tasks_json(request):
    """Return tasks as JSON for dashboard rendering."""
    tasks = Task.objects.filter(user=request.user).values(
        'id', 'title', 'description', 'status',
        'due_date', 'created_at', 'parser_confidence', 'delay_count'
    )
    task_list = []
    for t in tasks:
        t['due_date'] = t['due_date'].isoformat() if t['due_date'] else None
        t['created_at'] = t['created_at'].isoformat()
        task_list.append(t)
    return JsonResponse({'tasks': task_list})


def _calculate_streak(user):
    """Calculate consecutive days with at least one completed task."""
    today = timezone.localtime(timezone.now()).date()
    streak = 0
    day = today
    while True:
        has_completion = Task.objects.filter(
            user=user,
            status='completed',
            completed_at__date=day
        ).exists()
        if has_completion:
            streak += 1
            day -= timedelta(days=1)
        else:
            break
    return streak


def _productivity_score(user):
    """Weekly % of tasks completed on time."""
    week_ago = timezone.now() - timedelta(days=7)
    recent = Task.objects.filter(user=user, created_at__gte=week_ago)
    total = recent.count()
    if total == 0:
        return 0
    done = recent.filter(status='completed').count()
    return round((done / total) * 100)