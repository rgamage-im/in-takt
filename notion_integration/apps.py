from django.apps import AppConfig
import logging
import sys

from django.db.utils import OperationalError, ProgrammingError
from django.utils import timezone


logger = logging.getLogger(__name__)


def reconcile_stale_sync_jobs() -> int:
    """
    Mark orphaned queued/running sync jobs as failed on process startup.
    """
    from .models import NotionSyncJob

    now = timezone.now()
    stale = NotionSyncJob.objects.filter(
        status__in=[NotionSyncJob.STATUS_QUEUED, NotionSyncJob.STATUS_RUNNING],
        finished_at__isnull=True,
    )
    updated = stale.update(
        status=NotionSyncJob.STATUS_FAILED,
        finished_at=now,
        error_message="Job interrupted by app restart/redeploy.",
    )
    return updated


class NotionIntegrationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notion_integration"
    verbose_name = "Notion Integration"

    _reconciled_once = False

    def ready(self):
        # Django's autoreloader imports apps twice in dev; reconcile once per process.
        if NotionIntegrationConfig._reconciled_once:
            return
        NotionIntegrationConfig._reconciled_once = True

        management_commands_to_skip = {
            "makemigrations",
            "migrate",
            "collectstatic",
            "test",
            "shell",
            "createsuperuser",
        }
        if any(cmd in sys.argv for cmd in management_commands_to_skip):
            return

        try:
            updated = reconcile_stale_sync_jobs()
            if updated:
                logger.warning(
                    "notion_sync_startup_reconcile updated_jobs=%s status=failed reason=app_restart",
                    updated,
                )
        except (OperationalError, ProgrammingError):
            # DB tables may not exist during migrate/test setup.
            return
        except Exception:
            logger.exception("notion_sync_startup_reconcile_failed")
