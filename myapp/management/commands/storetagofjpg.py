from django.core.management.base import BaseCommand
from django.http import HttpResponse
from myapp.models import T5hawktags
from myapp.models import Companies
import urllib
import urllib2
import json
import socket
import os
import Image
import dlib
import glob
from skimage import io

class Command( BaseCommand ):
    def handle(self, *args, **options ):
        test_folder = args[0]
        outputpath = args[1]
        data = []
        brand = outputpath
        detector = dlib.simple_object_detector(outputpath)
        img_count = [ ]
        img_tags_count = [ ]
        img_name = { }
        img_tags = { }
        t5hawktags = [ ]
        t5hawkout = [ ]
        for f in glob.glob(os.path.join(test_folder,"*.jpg")):
            print("Processing file: {}".format(f))
            t5hawkout = []
            img = io.imread( f )
            dets = detector( img )
            image = os.path.basename(format(f))
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
            img_name = { 'count':format(len(dets)), 'name':image, 'tags': img_tags_count }
            img_count.append( img_name )
            data.append( img_count )
            print t5hawkout
            t5hawkout = json.dumps( t5hawkout )
            #try:
                #obj = T5hawktags.objects.get( picture = image, t5hawkbrand_id = 5 )
            #except T5hawktags.DoesNotExist:
                #obj = T5hawktags( picture = image, tag_count = format( len( dets ) ), tags = t5hawkout, brandName = brand, t5hawkbrand_id = 5,attribute = " " )
                #obj.save()
        self.stdout.write( json.dumps(data) )
