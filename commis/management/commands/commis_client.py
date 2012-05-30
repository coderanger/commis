import os
import sys
from optparse import make_option

from django.core.management.base import BaseCommand

from commis import conf

class Command(BaseCommand):
    help = 'Generate a Chef API client'

    option_list = BaseCommand.option_list + (
        make_option('-o', '--output',
            help='Path to write key.'),
        make_option('--validator', action='store_true', default=False,
            help='Generate a validator key'),
        make_option('-a', '--admin', action='store_true', default=False,
            help='Generate an admin client'),
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

    def handle(self, *args, **options):
        from commis.clients.models import Client
        output = options.get('output')
        if options.get('validator'):
            if args:
                sys.stderr.write('Error: --validator is mutually exclusive with name argument\n')
                return 1
            if options.get('admin'):
                sys.stderr.write('Error: --validator is mutually exclusive with --admin\n')
                return 1
            name = conf.COMMIS_VALIDATOR_NAME
            default_output = 'validation.pem'
        elif args:
            name = args[0]
            default_output = name + '.pem'
        else:
            sys.stderr.write('Error: No name specified\n')
            return 1

        if not output:
            output = default_output

        qs = Client.objects.filter(name=name)
        if qs.exists():
            if self.ask('A client named %s already exists. Would you like to create a new key?'%name, options):
                qs.delete()
            else:
                return
        if output != '-' and os.path.exists(output):
            if not self.ask('A file %s already exists. Would you like to overwrite it?'%output, options):
                return

        client = Client.objects.create(name=name, admin=bool(options.get('admin')))
        if output == '-':
            outf = self.stdout
        else:
            outf = open(output, 'wb')
        outf.write(client.key.private_export())
