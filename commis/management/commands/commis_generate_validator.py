import os
from optparse import make_option

from django.core.management.base import NoArgsCommand

from commis import conf

class Command(NoArgsCommand):
    help = 'Generate a validator client'

    option_list = NoArgsCommand.option_list + (
        make_option('-o', '--output',
            default='validator.pem',
            help='Path to write validator key.'),
        make_option('--noinput', action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'),
        make_option('--force', action='store_true', default=False,
            help='Continue despite the possibility of data loss.'),
        )

    def ask(self, msg, options):    
        interactive = options.get('interactive')
        force = options.get('force')

        if force:
            return True
        if interactive:
            confirm = None
            while not confirm or confirm[0] not in 'yn':
                try:
                    confirm = raw_input(msg+" [yN]").lower()
                except KeyboardInterrupt:
                    confirm = 'n'
                if not confirm:
                    confirm = 'n'
            return confirm[0] == 'y'
        else:
            return False

    def handle_noargs(self, **options):
        from commis.clients.models import Client
        output = options.get('output')
        name = conf.COMMIS_VALIDATOR_NAME

        qs = Client.objects.filter(name=name)
        if qs.exists():
            if self.ask('A client named %s already exists. Would you like to create a new key?'%name, options):
                qs.delete()
            else:
                return
        if output != '-' and os.path.exists(output):
            if not self.ask('A file %s already exists. Would you like to overwrite it?'%output, options):
                return

        client = Client.objects.create(name=name)
        if output == '-':
            outf = self.stdout
        else:
            outf = open(output, 'wb')
        outf.write(client.key.private_export())
