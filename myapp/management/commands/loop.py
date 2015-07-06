import os,sys
sys.path.append('/var/sites/thirdauth') # the parent directory of the project
sys.path.append('/var/sites/thirdauth') # these lines only needed if not on path
os.environ['DJANGO_SETTINGS_MODULE'] = 'thirdauth.settings'
from thirdauth import settings
from django.core.management.base import BaseCommand
from django.http import HttpResponse
from myapp.models import T5hawktags
import urllib
import urllib2
import json

class Command(BaseCommand):
    def handle(self, *args, **options):
        def hawktags( pageno ):
            print pageno
            count = 5
            #print count 
            if count == 5:
                if pageno < 3:
                    pageno = pageno + 1 
                    hawktags( pageno )
            return self.stdout.write("hawktags")
        hawktags( 1 )
        return self.stdout.write("handle")
    
