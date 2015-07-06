from django.core.management.base import BaseCommand
from django.http import HttpResponse
from myapp.models import T5hawktags
from myapp.models import Companies
from myapp.models import Picturetables
from myapp.models import Brands
from myapp.models import Paths
from myapp.models import Svms
from myapp.models import crons
import urllib
import urllib2
import json
import Image
import socket
import os
import dlib
import glob
from skimage import io
import time
import datetime
from datetime import date

class Command( BaseCommand ):
    
    def add_arguments(self, parser):
        parser.add_argument( 'fromdate' )
        parser.add_argument( 'todate' ) 
    
    def handle(self, *args, **options ):
    
        def TagImage( picName, name, imgName, count, attributes ):
                i = 1
                for svmName in svmNames:
                    t5hawkout = [ ]
                    brandName = svmName
                    outputpath = '/var/sites/thirdauth/static/test/'+svmName+'.svm'
                    detector = dlib.simple_object_detector( str( outputpath ) )
                    for f in glob.glob( os.path.join( test_folder, picName ) ):
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
                        HawkTags = { 'picture': name, 'tag_count':format( len( dets ) ), 'tags':t5hawkout, 'brandName': brandName, 't5hawkbrand_id':i, 'attributes': attributes   }
                        Hawk.append( HawkTags )
                        try:
                            obj = T5hawktags.objects.get( picture = name, brandName = brandName )
                            pictable = Picturetables.objects.all()
                        except T5hawktags.DoesNotExist:
                            obj = T5hawktags( picture = name, tag_count = format( len( dets ) ), tags = t5hawkout, brandName = brandName, t5hawkbrand_id = i,attribute = json.dumps( attributes ) )
                            obj.save()
                        #os.remove("static/test/"+imgName[0]+".jpg")
                    #print Hawk
                    #self.stdout.write(json.dumps(data))
                    sendtourl = "http://"+domainName+".bizom.in/activities/save35hawktags"
                    req = urllib2.Request(sendtourl, json.dumps( Hawk ), {'Content-Type': 'application/json'})
                    f = urllib2.urlopen( req )
                    response = f.read()
                    f.close()
                    i = i + 1
                return json.dumps(data)
        
        def DownloadImages( postDatum, bucket, count, counter ):
                for postData in postDatum:
                    attributes = { }
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
                            if not os.path.isfile( "/var/sites/thirdauth/static/test/"+img_name ):
                                if not os.path.isfile( "/var/sites/thirdauth/static/test/"+imgName[0]+".jpg" ):
                                    if img_name.endswith(('.png','PNG')):
                                        print ".png"
                                        urllib.urlretrieve( url, "/var/sites/thirdauth/static/test/"+img_name)
                                        try:
                                            print img_name
                                            im = Image.open("/var/sites/thirdauth/static/test/"+img_name)
                                            os.remove("/var/sites/thirdauth/static/test/"+img_name)
                                            im.save("/var/sites/thirdauth/static/test/"+imgName[0]+".jpg")
                                            picName = imgName[0]+".jpg"
                                        except:
                                            return json.dumps("Can't convert png to jpg")
                                    else:
                                        print ".jpg"
                                        urllib.urlretrieve(url, "/var/sites/thirdauth/static/test/"+img_name)
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
                    name = os.path.basename( url )
                    TagImage( picName, name, imgName, count, attributes )
                
                if count == 2:
                    counter += 1
                    if counter <= 3: 
                        makeurl( domainName, str( fromdate ), str( todate ), str(counter), tableName, counter )
        
        def makeurl( domainName, fromdate, todate, pageno, tableName, counter ):
                url = "http://"+domainName+".bizom.in/activities/getPictures?&fromdate="+fromdate+"&todate="+todate+"&pageno="+pageno+"&limit=2&tableName="+tableName
                print url
                req = urllib2.Request ( url )
                req.add_header('Accept', url )
                resp = urllib2.urlopen( req )
                content = resp.read()
                print content
                content = json.loads( content )
                error = content[ 'error' ][ 'code' ]
                if error == 404:
                    return self.stdout.write( "No data found for this date range.." )
                data = []
                attributes = { }
                count = content[ "data" ][ "count" ]
                bucket = content[ "data" ][ "bucket" ]
                postDatum = content[ "data" ][ "pictures" ]
                if postDatum != None:
                    DownloadImages( postDatum, bucket, count, counter )
                else:
                    return self.stdout.write( "No data found" )
    
            
    
        #fromdate = options[ 'fromdate' ]
        #todate = options[ 'todate' ]
        fromdate = args[ 0 ]
        todate = args[ 1 ]
        cronno = args[ 2 ]
        Hawk = []
        test_folder = "/var/sites/thirdauth/static/test/"
        if cronno == ' ':
            crones = crons.objects.all()
        else:
            crones = crons.objects.filter( id = int(cronno) )
        if crones.exists():
            for cron in crones:
                img_count = [ ]
                data = []
                img_tags_count = [ ]
                img_name = { }
                img_tags = { }
                t5hawktags = [ ]
                t5hawkout = [ ]
                HawkTags = { }
                Hawk = []
                counter = 1
                cronId = cron.id
                tableNames = cron.tablename
                isActive = cron.isactive
                domainName = cron.domainName
                svmPath = json.loads( cron.svmnames )
                svmNames = svmPath
                pageno = str( 1 )
                today = time.strftime("%Y-%m-%d %H:%M:%S")
                tableNames = json.loads(tableNames)
                for tableName in tableNames:
                    if fromdate != ' ':
                        if todate != ' ':
                            url = makeurl( domainName, str( fromdate ), str( todate ), pageno, tableName, counter )
                        else:
                            continue
                    else:
                        d1 = cron.fetchenddate
                        d2 = cron.fetchstartdate
                        newdate = d1 + datetime.timedelta(days=1)
                        fromdate = newdate.strftime('%Y-%m-%d')
                        todate = date.today()
                        makeurl( domainName, str( fromdate ), str( todate ), pageno, tableName, counter )
                print "fromdate"+str(fromdate)
                print "todate"+str(todate)
                print "domainName"+str(domainName)
                print pageno
                print tableName
                crons.objects.filter( id = cronId ).update( status = 0 )
                crons.objects.filter( id = cronId ).update( fetchstartdate = fromdate )
                crons.objects.filter( id = cronId ).update( fetchenddate = todate )
                crons.objects.filter( id = cronId ).update( fetchtime = today )
        print json.dumps(Hawk)
        return "done"
