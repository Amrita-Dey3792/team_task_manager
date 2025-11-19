from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Task, ActivityLog

_previous_values = {}

@receiver(pre_save, sender=Task)
def store_previous_values(sender, instance, **kwargs):
   
    if instance.pk:
        try:
            old_instance = Task.objects.get(pk=instance.pk)
            _previous_values[instance.pk] = {
                'assigned_to': old_instance.assigned_to,
                'status': old_instance.status
            }
        except Task.DoesNotExist:
            _previous_values[instance.pk] = {
                'assigned_to': None,
                'status': None
            }

@receiver(post_save, sender=Task)
def log_task_actions(sender, instance, created, **kwargs):

    if instance.is_deleted:
        return
    
    if created:
        ActivityLog.objects.create(
            action='task_created',
            performed_by=instance.created_by.user,
            team=instance.team,
            task=instance,
            details={'title': instance.title}
        )
    else:
        prev = _previous_values.get(instance.pk, {})
        
        if prev.get('status') and prev.get('status') != instance.status:
            ActivityLog.objects.create(
                action='task_status_changed',
                performed_by=instance.created_by.user,
                team=instance.team,
                task=instance,
                details={'old': prev.get('status'), 'new': instance.status}
            )
        
        if instance.pk in _previous_values:
            del _previous_values[instance.pk]