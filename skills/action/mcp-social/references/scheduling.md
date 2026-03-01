# Social Media Scheduling Best Practices

## Overview

This guide covers optimal posting times, scheduling strategies, and content calendar management for the Personal AI Employee's social media automation.

## Best Posting Times by Platform

### LinkedIn

```yaml
optimal_times:
  weekday:
    morning: "08:00-10:00"  # Business hours start
    lunch: "12:00-13:00"    # Lunch break browsing
    evening: "17:00-18:00"  # End of workday

  best_days:
    - Tuesday    # Highest engagement
    - Wednesday  # Strong engagement
    - Thursday   # Good engagement

  worst_days:
    - Saturday    # Lowest engagement
    - Sunday      # Low engagement

timezone: "America/New_York"  # Adjust to audience

optimal_frequency:
  posts_per_day: 1
  posts_per_week: 5
```

### Twitter/X

```yaml
optimal_times:
  weekday:
    morning: "08:00-09:00"   # Morning commute
    lunch: "12:00-13:00"     # Lunch break
    evening: "18:00-20:00"   # Evening browsing

  best_days:
    - Monday
    - Thursday
    - Friday

  weekend:
    morning: "09:00-10:00"   # Weekend morning

timezone: "America/New_York"

optimal_frequency:
  tweets_per_day: 3-5
  threads_per_week: 2-3
```

### Facebook

```yaml
optimal_times:
  weekday:
    morning: "09:00-10:00"
    lunch: "13:00-14:00"
    evening: "15:00-16:00"

  best_days:
    - Wednesday
    - Thursday
    - Friday

  weekend:
    afternoon: "12:00-14:00"

timezone: "America/New_York"

optimal_frequency:
  posts_per_day: 1-2
  posts_per_week: 5-7
```

### Instagram

```yaml
optimal_times:
  weekday:
    morning: "06:00-08:00"   # Early morning scroll
    lunch: "11:00-13:00"
    evening: "19:00-21:00"   # Evening prime time

  best_days:
    - Monday
    - Tuesday
    - Friday

  weekend:
    morning: "10:00-12:00"

timezone: "America/New_York"

optimal_frequency:
  posts_per_day: 1-2
  stories_per_day: 3-5
  reels_per_week: 2-3
```

## Scheduling Strategy

### Content Mix Ratio

```yaml
content_mix:
  linkedin:
    educational: 40%
    behind_scenes: 20%
    announcement: 15%
    promotional: 10%
    engagement: 15%

  twitter:
    educational: 30%
    engagement: 30%
    behind_scenes: 20%
    announcement: 10%
    promotional: 10%

  facebook:
    behind_scenes: 30%
    engagement: 30%
    educational: 20%
    announcement: 10%
    promotional: 10%

  instagram:
    behind_scenes: 35%
    lifestyle: 25%
    educational: 20%
    promotional: 10%
    engagement: 10%
```

### Frequency Guidelines

```python
def get_posting_schedule(platform):
    """Get recommended posting frequency for platform."""

    schedules = {
        'linkedin': {
            'max_per_day': 1,
            'min_per_week': 3,
            'optimal_per_week': 5,
            'min_gap_hours': 24
        },
        'twitter': {
            'max_per_day': 5,
            'min_per_week': 10,
            'optimal_per_week': 15,
            'min_gap_hours': 2
        },
        'facebook': {
            'max_per_day': 2,
            'min_per_week': 5,
            'optimal_per_week': 7,
            'min_gap_hours': 4
        },
        'instagram': {
            'max_per_day': 2,
            'min_per_week': 5,
            'optimal_per_week': 7,
            'min_gap_hours': 6
        }
    }

    return schedules.get(platform)
```

## Scheduling Workflow

### Phase 1: Content Creation

```python
def create_scheduled_post(platform, content, scheduled_time, media=None):
    """Create a scheduled post for later publication."""

    # 1. Validate content
    validation = validate_content(content, platform)
    if not validation['valid']:
        return {'error': validation['issues']}

    # 2. Check scheduling rules
    schedule_check = check_schedule_rules(platform, scheduled_time)
    if not schedule_check['valid']:
        # Suggest better time
        suggested_time = get_optimal_time(platform, scheduled_time)
        return {'error': schedule_check['reason'], 'suggested_time': suggested_time}

    # 3. Create scheduled file
    schedule_id = generate_schedule_id()
    scheduled_file = create_scheduled_file({
        'id': schedule_id,
        'platform': platform,
        'content': content,
        'scheduled_time': scheduled_time,
        'media': media,
        'created': now()
    })

    # 4. Add to queue
    add_to_scheduled_queue(scheduled_file)

    return {
        'status': 'scheduled',
        'schedule_id': schedule_id,
        'file': str(scheduled_file),
        'scheduled_time': scheduled_time
    }
```

### Phase 2: Schedule Processing

```python
def process_scheduled_posts():
    """Process posts scheduled for current time."""

    now = get_current_time()
    due_posts = get_due_posts(now)

    for post in due_posts:
        try:
            # Get MCP server
            server = get_mcp_server(post['platform'])

            # Execute post
            result = server.handle_request(post['operation'], {
                'content': post['content'],
                'media_path': post.get('media')
            })

            if result['status'] == 'posted':
                # Move to Done
                move_to_done(post)
                log_success(post, result)
            else:
                # Handle error
                handle_post_error(post, result)

        except Exception as e:
            handle_exception(post, e)
```

### Phase 3: Post-Publication

```python
def post_publication(post, result):
    """Handle post-publication tasks."""

    # 1. Log the action
    log_action({
        'operation': 'scheduled_post',
        'platform': post['platform'],
        'schedule_id': post['id'],
        'result': result,
        'timestamp': now()
    })

    # 2. Update metrics
    update_dashboard({
        'platform': post['platform'],
        'posts_today': increment('posts_today'),
        'last_post': now()
    })

    # 3. Schedule engagement check
    schedule_engagement_check(post['id'], delay_hours=24)

    # 4. Clean up
    archive_scheduled_file(post)
```

## Scheduled File Format

```markdown
---
type: scheduled_post
id: SCHED_20260301_103000
platform: linkedin
scheduled_time: 2026-03-02T09:00:00Z
created: 2026-03-01T10:30:00Z
status: pending
media: /vault/media/project_image.jpg
tags: [announcement, product]
---

Excited to share our latest project milestone! 🎉

Key achievements:
- 50% improvement in efficiency
- Team collaboration at its best
- Innovation driving results

#innovation #teamwork #projectmanagement
```

## Time Zone Handling

```python
def convert_to_utc(local_time, timezone):
    """Convert local time to UTC for scheduling."""
    from zoneinfo import ZoneInfo
    from datetime import datetime

    local_dt = datetime.fromisoformat(local_time)
    local_dt = local_dt.replace(tzinfo=ZoneInfo(timezone))

    utc_dt = local_dt.astimezone(ZoneInfo('UTC'))
    return utc_dt.isoformat()

def get_user_local_time(utc_time, timezone):
    """Convert UTC to user's local time."""
    from zoneinfo import ZoneInfo
    from datetime import datetime

    utc_dt = datetime.fromisoformat(utc_time)
    utc_dt = utc_dt.replace(tzinfo=ZoneInfo('UTC'))

    local_dt = utc_dt.astimezone(ZoneInfo(timezone))
    return local_dt.isoformat()
```

## Engagement Tracking

### Scheduled Checks

```python
def schedule_engagement_check(post_id, delay_hours=24):
    """Schedule engagement metrics check."""

    check_time = now() + timedelta(hours=delay_hours)

    create_engagement_task({
        'post_id': post_id,
        'scheduled_time': check_time,
        'metrics': ['likes', 'comments', 'shares', 'clicks']
    })

def check_engagement(post_id):
    """Check engagement metrics for a post."""

    post = get_post(post_id)
    platform = post['platform']

    # Get metrics from platform
    metrics = get_platform_metrics(platform, post['platform_id'])

    # Store metrics
    store_engagement_data(post_id, metrics)

    # Check for low engagement
    if metrics['engagement_rate'] < get_threshold(platform, 'low_engagement'):
        alert_low_engagement(post_id, metrics)

    return metrics
```

### Engagement Thresholds

```yaml
engagement_thresholds:
  linkedin:
    good: 2%  # Engagement rate
    average: 1%
    low: 0.5%

  twitter:
    good: 0.5%  # Engagement rate
    average: 0.2%
    low: 0.1%

  facebook:
    good: 0.1%  # Engagement rate
    average: 0.05%
    low: 0.02%

  instagram:
    good: 3%  # Engagement rate
    average: 1.5%
    low: 0.5%
```

## Content Calendar Integration

### Weekly View

```markdown
## Week of 2026-03-02

| Day       | LinkedIn          | Twitter           | Facebook        |
|-----------|-------------------|-------------------|-----------------|
| Monday    | -                 | Quick tip         | -               |
| Tuesday   | Industry insight  | Thread            | Behind scenes   |
| Wednesday | Team spotlight    | Engagement post   | Value post      |
| Thursday  | Value post        | Announcement      | Question        |
| Friday    | Weekly recap      | Casual            | Weekend preview |
```

### API Integration

```python
def get_weekly_schedule(start_date):
    """Get scheduled posts for the week."""

    end_date = start_date + timedelta(days=7)

    scheduled = get_scheduled_posts(start_date, end_date)

    calendar = {}
    for post in scheduled:
        day = post['scheduled_time'].date().isoformat()
        platform = post['platform']

        if day not in calendar:
            calendar[day] = {}

        if platform not in calendar[day]:
            calendar[day][platform] = []

        calendar[day][platform].append(post)

    return calendar
```

## Conflict Resolution

```python
def resolve_scheduling_conflicts(new_post, existing_posts):
    """Resolve conflicts when scheduling new posts."""

    conflicts = []
    platform = new_post['platform']

    for post in existing_posts:
        # Check if same platform and close time
        if post['platform'] == platform:
            time_diff = abs(new_post['scheduled_time'] - post['scheduled_time'])

            min_gap = get_min_gap_hours(platform) * 3600

            if time_diff.total_seconds() < min_gap:
                conflicts.append(post)

    if conflicts:
        # Suggest alternative times
        alternatives = suggest_alternative_times(platform, new_post['scheduled_time'])

        return {
            'status': 'conflict',
            'conflicts': conflicts,
            'suggestions': alternatives
        }

    return {'status': 'ok'}
```