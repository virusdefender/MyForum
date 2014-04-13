#coding=utf-8
from Forum.models import Zone, ZoneManager


def is_manager(zone_id, username):
    try:
        ZoneManager.objects.get(username=username, zone__id=zone_id)
    except ZoneManager.DoesNotExist:
        return False
    return True


