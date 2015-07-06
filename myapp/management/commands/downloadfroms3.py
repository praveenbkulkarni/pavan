from django.core.management.base import BaseCommand
from django.http import HttpResponse
import urllib
import urllib2
import json
import socket
import os


class Command( BaseCommand ):
    def handle(self, *args, **options ):
        postDatum = ["pics192801430447137.png","pics192901430447137.png","pics193001430447137.png","pics47001430450351.png","pics47101430450351.png","pics47201430450351.png","pics401701430451396.png","pics498101430451531.png","pics498201430451532.png","pics498301430451532.png","pics851001430451540.png"]
        bucket = "https://s3-ap-southeast-1.amazonaws.com/omspics/"
        for postData in postDatum:
            print postData
            imgName = postData
            url = bucket + imgName
            attempts = 0
            print url
            storePath = "static/test/"+imgName
            while attempts <= 3:
                timeout = 30
                socket.setdefaulttimeout( timeout )
                try:
                    if not os.path.isfile( storePath  ):
                        urllib.urlretrieve( url, storePath )
                    else:
                        attempts = 5
                except:
                    attempts += 1
                    print "except"
            print postData
        return self.stdout.write( "saved" )
