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
        try:
            url = "http://stagingadpl.bizom.in/activities/getPictures?&fromdate=2014-07-01&todate=2014-09-01&pageno=6&limit=10&tableName=activitypictures"
            req = urllib2.Request ( url )
            req.add_header('Accept', url )
            resp = urllib2.urlopen( req )
            content = resp.read()
            content = json.loads( content )
        except:
            self.stdout.write("Internet connection too slow..!!")
        datas = content[ 'data' ][ 'pictures' ]
        HawkTags = { }
        attributes = { }
        Hawk = []
        for data in datas:
            tagdatas = T5hawktags.objects.filter( picture = data[ 'img_name' ], t5hawkbrand_id = 1, erp_id = 1  )
            if tagdatas.exists():
                for tagdata in tagdatas:
                    picture = tagdata.picture
                    tag_count = tagdata.tag_count
                    tags = tagdata.tags
                    t5hawkbrand_id = tagdata.t5hawkbrand_id
                    brandName = tagdata.brandName
                    attribute = tagdata.attribute
                    HawkTags = { 'picture': picture, 'tag_count':tag_count, 'tags':tags, 'brandName': brandName, 't5hawkbrand_id':t5hawkbrand_id, 'attributes':json.loads( attribute )  }
                    Hawk.append( HawkTags )
        self.stdout.write(json.dumps(Hawk))
        
