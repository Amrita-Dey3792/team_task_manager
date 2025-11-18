from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Task, ActivityLog

@receiver(post_save, sender=Task)
def log_task_actions(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            action='task_created',
            performed_by=instance.created_by.user,
            team=instance.team,
            task=instance,
            details={'title': instance.title}
        )
    elif instance.assigned_to and instance.tracker.has_changed('assigned_to'):
        ActivityLog.objects.create(
            action='task_assigned',
            performed_by=instance.created_by.user,
            team=instance.team,
            task=instance,
            target_user=instance.assigned_to.user if instance.assigned_to else None
        )
    elif instance.tracker.has_changed('status'):
        ActivityLog.objects.create(
            action='task_status_changed',
            performed_by=instance.created_by.user,
            team=instance.team,
            task=instance,
            details={'old': instance.tracker.previous('status'), 'new': instance.status}
        )