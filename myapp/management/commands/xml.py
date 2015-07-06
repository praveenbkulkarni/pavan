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
import myapp.xml.etree.ElementTree as ET

class Command( BaseCommand ):
    def handle(self, *args, **options ):
        
        tree = ET.parse('training.xml')
        root = ET.fromstring(tree)

        # Top-level elements
        print root.findall(".")
        

        # All 'neighbor' grand-children of 'country' children of the top-level
        # elements
        root.findall("./country/neighbor")

        # Nodes with name='Singapore' that have a 'year' child
        root.findall(".//year/..[@name='Singapore']")

        # 'year' nodes that are children of nodes with name='Singapore'
        root.findall(".//*[@name='Singapore']/year")

        # All 'neighbor' nodes that are the second child of their parent
        root.findall(".//neighbor[2]")
        
