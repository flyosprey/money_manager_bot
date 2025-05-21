import json

from django_celery_beat.models import CrontabSchedule, PeriodicTask

from tbot.dto.ai.type import ADVICE_ARGS_BY_TYPE, AdviceType

weekly_schedule, _ = CrontabSchedule.objects.get_or_create(
    minute="0",
    hour="9",
    day_of_week="1",  # 0 = Sunday, 1 = Monday
    day_of_month="*",
    month_of_year="*",
)


PeriodicTask.weekly_schedule.create(
    crontab=weekly_schedule,
    name="Give weekly advice",
    task="money_manager.tasks.ai_advice",
    args=json.dumps([]),
    kwargs=json.dumps(ADVICE_ARGS_BY_TYPE[AdviceType.MONTHLY.value]),
    enabled=True,
)


monthly_schedule, _ = CrontabSchedule.objects.get_or_create(
    minute="0",
    hour="9",
    day_of_month="1",
    month_of_year="*",
    day_of_week="*",
)

PeriodicTask.objects.create(
    interval=monthly_schedule,
    name="Give monthly advice",
    task="money_manager.tasks.ai_advice",
    args=json.dumps([]),
    kwargs=json.dumps(ADVICE_ARGS_BY_TYPE[AdviceType.MONTHLY.value]),
    enabled=True,
)
