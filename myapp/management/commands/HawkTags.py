from django.core.management.base import BaseCommand
from django.http import HttpResponse
from myapp.models import T5hawktags
from myapp.models import Companies
from myapp.models import Picturetables
from myapp.models import Brands
from myapp.models import Paths
from myapp.models import Svms
import urllib
import urllib2
import json
import Image
import socket
import os
import dlib
import glob
from skimage import io

class Command( BaseCommand ):
    def handle(self, *args, **options ):
        def hawktags( pageno ):
            picturetables = Picturetables.objects.all()
            if picturetables.exists():
                for picturetable in picturetables:
                    picturetableId = picturetable.id
                    tableName = picturetable.tablename
                    isactive = picturetable.isactive
                    todate = '' 
                    fromdate = ''
                    brandId = picturetable.brand_id
                    companyId = picturetable.company_id
                    brands = Brands.objects.get( id = brandId )
                    brandName = brands.name
                    companies = Companies.objects.get( id = companyId )
                    domainName = companies.domainname
                    paths = Paths.objects.get( id = brandId )
                    svmPath = paths.svm_path
                    svms = Svms.objects.get( brand_id = brandId, isdefault = 1  )
                    svmName = svms.svm_name
                return
            brands_id = 2
            print pageno
            url = "http://stagingadpl.bizom.in/activities/getPictures?&fromdate=2014-07-01&todate=2014-09-01&pageno="+str(pageno)+"&limit=2&tableName=activitypictures"
            req = urllib2.Request ( url )
            req.add_header('Accept', url )
            resp = urllib2.urlopen( req )
            content = resp.read()
            content = json.loads( content )
            print content
            error = content[ 'result' ]
            if error != True:
                return self.stdout.write( "No data found for this date range.." )
            data = []
            attributes = { }
            count = content[ "data" ][ "count" ]
            bucket = content[ "data" ][ "bucket" ]
            postDatum = content[ "data" ][ "pictures" ]
            print postDatum
            for postData in postDatum:
                img_name = postData[ 'img_name' ]
                activity_ids = postData[ 'activity_id' ]
                ids = postData[ 'id' ]
                for key, val in postData.iteritems():
                    if key !='img_name':
                        if key !='id':
                            attributes[ key ] = val
                        if key == 'id':
                            attributes[ tableName+"_"+ key ] = val
                url = bucket + img_name
                attempts = 0
                imgName = img_name.split( '.' )
                while attempts <= 3:
                    timeout = 30
                    socket.setdefaulttimeout(timeout)
                    try:
                        if not os.path.isfile( "static/test/"+img_name ):
                            if not os.path.isfile( "static/test/"+imgName[0]+".jpg" ):
                                if img_name.endswith(('.png','PNG')):
                                    print ".png"
                                    urllib.urlretrieve(url, "static/test/"+img_name)
                                    try:
                                        im = Image.open("static/test/"+img_name)
                                        os.remove("static/test/"+img_name)
                                        im.save("static/test/"+imgName[0]+".jpg")
                                        picName = imgName[0]+".jpg"
                                    except:
                                        return json.dumps("Can't convert png to jpg")
                                else:
                                    print ".jpg"
                                    urllib.urlretrieve(url, "static/test/"+img_name)
                                    picName = img_name
                            else:
                                print "m here"
                                attempts = 4
                                picName = imgName[0]+".jpg"
                        else:
                            print "m here"
                            attempts = 4
                            picName = img_name
                    except:
                        attempts += 1
                        print "except"
                brand = "adpl"
                brand = brand.lower()
                print brand
                if (brand <> 'engage_fem' and brand <> 'adpl' and brand <> "engage_men"):
                    return HttpResponse(json.dumps("Enter valid brand name ex: engage_men, engage_fem, adpl"))
                if brand == 'engage_fem':
                    outputpath = "engage_fem.svm"
                elif brand == 'engage_men':
                    outputpath = "engage_men.svm"
                else:
                    outputpath = "ruslan.svm"
                name = os.path.basename(url)
                test_folder = "/var/sites/thirdauth/static/test/"
                detector = dlib.simple_object_detector(outputpath)
                img_count = [ ]
                img_tags_count = [ ]
                img_name = { }
                img_tags = { }
                t5hawktags = [ ]
                t5hawkout = [ ]
                print picName
                for f in glob.glob(os.path.join(test_folder,picName)):
                    print("Processing file: {}".format(f))
                    img = io.imread( f )
                    dets = detector( img )
                    print("Number of Objects detected: {}".format( len( dets ) ) )
                    for k, d in enumerate( dets ):
                        print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(k, d.left(), d.top(), d.right(), d.bottom()))
                        img_tags = { 'left': format( d.left() ),'top': format( d.top() ),'right': format( d.right() ),'bottom': format( d.bottom() ),'count': format( len(dets) ) }
                        t = int( format( d.top() ) )
                        l = int( format( d.left() ) ) 
                        w = abs( int( format( d.right() ) ) - int( format( d.left() ) ) )
                        h = abs( int( format( d.top() ) ) - int( format( d.bottom() ) ) )
                        t5hawktags = [ t, l, w, h ]
                        t5hawkout.append( t5hawktags )
                        img_tags_count.append( img_tags )
                    img_name = { 'count':format(len(dets)), 'name':name, 'tags': img_tags_count }
                    img_count.append( img_name )
                    data.append( img_count )
                    t5hawkout = json.dumps( t5hawkout )
                    try:
                        obj = T5hawktags.objects.get( picture = name, t5hawkbrand_id = brands_id )
                    except T5hawktags.DoesNotExist:
                        obj = T5hawktags( picture = name, tag_count = format( len( dets ) ), tags = t5hawkout, brandName = brand, t5hawkbrand_id = brands_id,attribute = json.dumps( attributes ) )
                        obj.save()
                    os.remove("static/test/"+imgName[0]+".jpg")
            if count == 100:
                if pageno < 3:
                    pageno = pageno + 1
                    hawktags( pageno )
            self.stdout.write(json.dumps(data))
            return json.dumps(data)
        self.stdout.write( hawktags( 1 ) )
