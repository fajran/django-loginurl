from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = "Clean up expired one time keys."

    def handle_noargs(self, **options):
        from onetime import utils
        utils.cleanup()

