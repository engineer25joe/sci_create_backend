"""
Manually grant credits to a workspace for testing. Usage:
  python manage.py grant_credits --workspace-id <uuid> --amount 50
"""
from django.core.management.base import BaseCommand, CommandError

from apps.identity.models import Workspace
from services.billing_service.service import grant_credits


class Command(BaseCommand):
    help = "Grant AI credits to a workspace (for testing/manual admin use)."

    def add_arguments(self, parser):
        parser.add_argument("--workspace-id", required=True)
        parser.add_argument("--amount", type=int, required=True)
        parser.add_argument("--reason", default="Manual grant")

    def handle(self, *args, **options):
        workspace = Workspace.objects.filter(id=options["workspace_id"]).first()
        if workspace is None:
            raise CommandError(f"No workspace found with id {options['workspace_id']}")

        grant_credits(workspace=workspace, amount=options["amount"], reason=options["reason"])
        self.stdout.write(self.style.SUCCESS(f"Granted {options['amount']} credits to {workspace.name}"))
