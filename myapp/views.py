from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import HttpRequest
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
import urllib
import urllib2
import json
import shutil
import os
import Image
import socket
import wget
import socket
import fnmatch
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
import xml.etree.ElementTree as ET
from django.forms import ModelForm
from .models import Brands,T5hawktags
from .models import Buckets
from .models import Companies
from .models import Picturetypes
from .models import Paths
from .models import Pictures
from .models import Picturetables
from .models import Tags
from .models import Users
from .models import Document
from .models import Svms
from .forms import CompayForm
from .forms import BrandForm
from .forms import BrandEditForm
from .forms import DocumentForm
from skimage import io
import glob
import dlib
import base64
import time
from os.path import relpath

def check(request):
    HOSTNAME = 'http://' + request.get_host()
    oAUTHURL = "http://stagingapi.bizom.in/oauth/client?return_url=" + urllib.unquote(HOSTNAME).decode('utf8')
    print("Location:"+oAUTHURL)
    url=str(oAUTHURL)
    a_t=None
    a_t=request.GET.get('access_token')
    if (a_t != None):
        mid = "http://stagingapi.bizom.in/users/getuserinfo?access_token=" + str(a_t)
        req = urllib2.Request (mid)
        req.add_header('Accept', mid)
        resp = urllib2.urlopen(req)
        content = resp.read()
        data = json.loads(content)
        company_name = data["Company"]["name"]
        erp=data["Company"]["id"]
        domainname = data[ 'Company' ][ 'domainname' ]
        request.session["role_id"] = data["Role"]["id"]
        request.session["user"] = erp
        user = request.session["user"]
        print("hello"+user)
        #company_name = base64.urlsafe_b64encode(c_name)
        if Companies.objects.filter(erp_id=erp):
            return HttpResponseRedirect('/Home')
        else:
            usr=Users(name=user,company_id=erp)
            usr.save()
            cmp=Companies( name = company_name, erp_id = erp, domainname = domainname )
            cmp.save()
            print "create Folder"
            company_folder = settings.MEDIA_ROOT +"/companies/"+ company_name
            if not os.path.exists(company_folder):
                os.makedirs(company_folder)
                os.makedirs(company_folder+"/images")
            return HttpResponseRedirect('/Home')
    else:
        return HttpResponseRedirect(url)

def company_list(request, template_name='myapp/company_list.html'):
    if 'user' in request.session:
        user = request.session['user']
        role_id = request.session['role_id']
        print user
        data = {}
        if role_id != '1':
            companies = Companies.objects.filter(erp_id = user)
            data['a_show'] = 'ahide'
        else:
            companies = Companies.objects.all()
            data['a_show'] = 'ashow'
        data['object_list'] = companies
        print data
        return render(request, template_name, data)
    else:
        return redirect('/')

def brand_list(request,pk,template_name='myapp/brand_list.html'):
    company = get_object_or_404(Companies, pk=pk)
    if request.method == 'GET':
        print company.name
        brand = Brands.objects.filter(company_id = company.id)
        data = {}
        data['object_list'] = brand
        data['pk'] = pk
        data[ 'domainname' ] = company.domainname
        return render(request, template_name, data)
    else:
        return render(request,template_name)

def brand_create(request,pk,template_name='brand_form.html'):
    form = BrandForm(request.POST or None, initial={"company_id": pk})
    if form.is_valid():
        print settings.MEDIA_ROOT
        form_data = form.cleaned_data
        companies = Companies.objects.filter(id = pk)
        for company in companies:
            company_name = company.name
        brand_folder = settings.MEDIA_ROOT +"/companies/"+ company_name +"/"+ form_data['name']
        company_folder = settings.MEDIA_ROOT +"/companies/"+ company_name +"/images"
        if not os.path.exists(brand_folder):
            os.makedirs(brand_folder)
            os.makedirs(brand_folder+"/train")
            os.makedirs(brand_folder+"/test")
            os.makedirs(brand_folder+"/demo")
            os.makedirs(brand_folder+"/svm")
        form.save()
        b_id=Brands.objects.latest('id')
        print b_id.id
        paths=Paths(train_path = brand_folder+"/train", test_path = brand_folder+"/test",demo_path = brand_folder+"/demo",svm_path = brand_folder+"/svm", brand_id = b_id.id, company_id = pk, company_path = company_folder )
        paths.save()
        return redirect('brand_list',pk)
    return render(request, template_name, {'form':form})

def company_create(request,template_name='company_form.html'):
    form = CompayForm(request.POST or None)
    if form.is_valid():
        form_data = form.cleaned_data
        company_name = form_data['name']
        company_folder = settings.MEDIA_ROOT +"/companies/"+ company_name
        if not os.path.exists(company_folder):
            os.makedirs(company_folder)
        form.save()
        return redirect('company_list')
    return render(request, template_name, {'form':form})

def brand_update(request, pk, template_name='brand_edit_form.html'):
    brand = get_object_or_404(Brands, pk=pk)
    form = BrandEditForm(request.POST or None, instance=brand)
    companies = Companies.objects.filter( id = brand.company_id )
    if companies.exists():
        for company in companies:
            companyId = company.id
    if form.is_valid():
        form.save()
        return redirect( 'brand_list', companyId )
    return render(request, template_name, {'form':form})

def brand_delete(request, pk, template_name='brand_confirm_delete.html'):
    brand = get_object_or_404(Brands, pk=pk)
    if request.method=='POST':
        companies = Companies.objects.filter( id = brand.company_id )
        if companies.exists():
            for company in companies:
                companyName = company.name
        shutil.rmtree(settings.MEDIA_ROOT+'/companies/'+companyName+'/'+brand.name)
        brand.delete()
        return redirect('brand_list',brand.company_id)
    return render(request, template_name, {'object': brand})

@never_cache
def select_image(request,pk,op,template_name='select_image.html'):
    brand = Brands.objects.filter( id = pk )
    paths = Paths.objects.filter(brand_id = pk)
    if paths.exists():
        for pt in paths:
            test = pt.test_path
            train = pt.train_path
            if not os.path.exists(test):
                os.makedirs(test)
                os.makedirs(train)
    else:
        test = settings.MEDIA_ROOT+"/cuba/test"
        train = settings.MEDIA_ROOT+"/cuba/train"
    data = {}
    data[ 'object_list' ] = brand
    if brand.exists():
        for brands in brand:
            cmp_id = brands.company_id
    if (op == 'train'):
        path = train
    else:
        path = test
    files = []
    for file in os.listdir( path ):
        if file.endswith( ('.jpg', '.JPG', '.jpeg', 'JPEG', '.png', '.PNG') ):
            files.append( file )
    data[ 'file_name' ] = files
    path = os.path.relpath(path, settings.MEDIA_ROOT)
    data[ 'path' ] = "/"+str(path)+"/"
    data[ 'file_path' ] = settings.MEDIA_ROOT+"/"+path+"/"
    data[ 'pk' ] = pk
    data[ 'cmp_id' ] = cmp_id
    print "rel path"+str(path)
    print settings.MEDIA_ROOT+path
    return render(request, template_name,data)
    return HttpResponseRedirect('/Home')

def upload_img(request,pk,template_name='upload_img.html'):
    brand = get_object_or_404(Brands, pk=pk)
    paths=Paths.objects.filter(brand_id = brand.id)
    print paths
    for pats in paths:
        test_path = pats.test_path
        train_path = pats.train_path
        demo_path = pats.demo_path
    #print demo_path
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            for afile in request.FILES.getlist('docfile'):
                Document(docfile = afile ).save()
                if request.POST.get('test'):
                    buffer_size=16000
                    fsrc=open(settings.MEDIA_ROOT+"/train/"+str(afile), 'rb')
                    fdest=open(test_path+"/"+str(afile), 'wb')
                    shutil.copyfileobj(fsrc, fdest, buffer_size)
                    os.remove(settings.MEDIA_ROOT+"/train/"+str(afile))
                if request.POST.get('train'):
                    buffer_size=16000
                    fsrc=open(settings.MEDIA_ROOT+"/train/"+str(afile), 'rb')
                    fdest=open(train_path+"/"+str(afile), 'wb')
                    shutil.copyfileobj(fsrc, fdest, buffer_size)
                    os.remove(settings.MEDIA_ROOT+"/train/"+str(afile))
                if request.POST.get('demo'):
                    buffer_size=16000
                    fsrc=open(settings.MEDIA_ROOT+"/train/"+str(afile), 'rb')
                    fdest=open(demo_path+"/"+str(afile), 'wb')
                    shutil.copyfileobj(fsrc, fdest, buffer_size)
                    os.remove(settings.MEDIA_ROOT+"/train/"+str(afile))
            return HttpResponse("save")
            return render(request,template_name,{'form': form,'brands':brand},context_instance=RequestContext(request))
            return HttpResponseRedirect(reverse('myapp.views.upload_img'))
    else:
        form = DocumentForm()
        documents = Document.objects.all()
        brand = get_object_or_404(Brands, pk=pk)
        return render(
            request,template_name,
            {'documents': documents, 'form': form,'brands':brand},
            context_instance=RequestContext(request)
        )

def ajax(request, pk, op, template_name='select_image.html'):
   if request.POST.has_key('client_response'):
        def indent(elem, level=0):
            i = "\n" + level*"  "
            if len(elem):
                if not elem.text or not elem.text.strip():
                    elem.text = i + "  "
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
                for elem in elem:
                    indent(elem, level+1)
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
            else:
                if level and (not elem.tail or not elem.tail.strip()):
                    elem.tail = i
        
        if str( op ) == 'save':
            data = request.POST['client_response']
            path = request.POST['path']
            response_dict = {}
            response_dict = data
            data = json.loads(data)
            i = 0
            print data
            dataset = Element( 'dataset' )
            images = SubElement( dataset, 'images')
            print "filepath1  "+path
            brands = Brands.objects.filter( id = pk )
            if brands.exists():
                for brand in brands:
                    c_id = brand.company_id
            for pic in data:
                print pic
                image = SubElement( images, 'image' , file = path+str(pic))
                Pictures( picture_name = str(pic) , bucket_id = 1 , picturetable_id = 1 , imagetype_id = 1 , brand_id = pk, company_id = c_id ).save()
                for color in data[pic].iteritems():
                    #print color
                    (x,y) = color
                    print y
                    for tags1 in y:
                        tags = y[tags1]
                        SubElement( image , 'box', top = ""+str(tags['t'])+"" , left = ""+str(tags['l'])+"" , width = ""+str(tags['w'])+"", height = ""+str(tags['h'])+"" )
                        p_id=Pictures.objects.latest('id')
                        print p_id.id
                        Tags( top = tags['t'], left = tags['l'], width = tags['w'], height = tags['h'], picture_id = p_id.id ).save()
            output_file = open( path+'training.xml', 'w' )
            output_file.write( '<?xml version="1.0" encoding="ISO-8859-1"?>' )
            indent( dataset )
            output_file.write( ElementTree.tostring( dataset ) )
            output_file.close()
            return HttpResponse("Saved")
        else:
            path = request.POST['path']
            tree = ET.parse( path+'training.xml')
            root = tree.getroot()
            data = request.POST['client_response']
            response_dict = {}
            response_dict = data
            data = json.loads(data)
            i = 0
            print data
            element = root.find('images')
            print "filepath1  "+path
            brands = Brands.objects.filter( id = pk )
            if brands.exists():
                for brand in brands:
                    c_id = brand.company_id
            for pic in data:
                print pic
                find = path+str(pic)
                removeList = [ ]
                subelement = element.findall(".//*[@file='find']")
                for child in element.iter('image'):
                    if (child.tag == 'image'): 
                        name = child.attrib['file']
                    if ( name == find ):
                        removeList.append( child )
                for tag in removeList:
                    element.remove( tag )
                if not subelement:
                    image = SubElement( element, 'image' , file = path+str(pic))
                    Pictures( picture_name = str(pic) , bucket_id = 1 , picturetable_id = 1 , imagetype_id = 1 , brand_id = pk, company_id = c_id ).save()
                    for color in data[pic].iteritems():
                        #print color
                        (x,y) = color
                        print y
                        for tags1 in y:
                            tags = y[tags1]
                            SubElement( image , 'box', top = ""+str(tags['t'])+"" , left = ""+str(tags['l'])+"" , width = ""+str(tags['w'])+"", height = ""+str(tags['h'])+"" )
                            p_id=Pictures.objects.latest('id')
                            print p_id.id
                            Tags( top = tags['t'], left = tags['l'], width = tags['w'], height = tags['h'], picture_id = p_id.id ).save()
            output_file = open( path+'training.xml', 'w' )
            output_file.write( '<?xml version="1.0" encoding="ISO-8859-1"?>' )
            indent( root )
            output_file.write( ElementTree.tostring( root ) )
            output_file.close()
            return HttpResponse("Saved")
        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')
   else:
        return render(request,template_name, context_instance=RequestContext(request))

@never_cache
def demo( request, pk, template_name = 'myapp/demo.html' ):
    brand = get_object_or_404( Brands, pk = pk )
    paths = Paths.objects.filter( brand_id = pk )
    if paths.exists():
        for pt in paths:
            path = pt.demo_path
    svms = Svms.objects.filter( brand_id = pk )
    data = { }
    data[ 'file_name' ] = os.listdir( path )
    path = os.path.relpath(path, settings.MEDIA_ROOT)
    data[ 'path' ] = "/"+str(path)+"/"
    data[ 'file_path' ] = settings.MEDIA_ROOT+"/"+path+"/"
    data[ 'pk' ] = pk
    data[ 'svms' ] = svms
    data[ 'cmp_id' ] = brand.company_id
    return render( request, template_name, data, context_instance = RequestContext( request ) )

def operation( request, url, template_name= 'operation.html' ):
    return HttpResponse( url )
    return render( request, template_name )

def result( request, pk, svm ):
    brand = get_object_or_404( Brands, pk = pk )
    if request.POST.has_key( 'client_response' ):
        data = request.POST[ 'client_response' ]
        response_dict = {}
        response_dict[ 'tags' ] = {}
        print svm
        paths = Paths.objects.filter( brand_id = pk )
        if paths.exists():
            for pt in paths:
                dpath = pt.demo_path
                svmpath = pt.svm_path
        #svms = Svms.objects.filter( brand_id = pk ).latest( 'id' )
        svmname = svm+".svm"
        print svmname
        test_folder = dpath
        outputpath = svmpath +"/"+ svmname
        if not os.path.exists(outputpath):
            return HttpResponse("File has been deleted")
        fileformat = "jpg"
        print outputpath
        detector = dlib.simple_object_detector( str(outputpath) )
        for f in glob.glob( os.path.join( test_folder, data ) ):
            print("Processing file: {}".format(f))
            img = io.imread(f)
            dets = detector(img)
            print("Number of Objects detected: {}".format(len(dets)))
            for k, d in enumerate(dets):
                print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(k, d.left(), d.top(), d.right(), d.bottom()))
                response_dict['tags'][ k ] = { 'name':data,'l': format(d.left()),'t': format(d.top()),'r': format(d.right()),'b': format(d.bottom()),'count': format(len(dets)) }
        return HttpResponse(json.dumps(response_dict))
    else:
        return render(request,template_name, context_instance=RequestContext(request))

def create_svm(request,pk,template_name='create_svm.html'):
     brand = get_object_or_404(Brands, pk=pk)
     data = {}
     data[ 'pk' ] = pk
     if request.method == 'POST':
        svm = request.POST.get('svm')
        cval = request.POST.get('cval')
        paths = Paths.objects.filter( brand_id = pk )
        if paths.exists():
            for pt in paths:
                train_path = pt.train_path
                train_path = os.path.relpath(train_path,settings.MEDIA_ROOT)
                test_path = pt.test_path
                test_path = os.path.relpath(test_path,settings.MEDIA_ROOT)
                svm_path = pt.svm_path
        #cmd = "python 35Hawkdetect.py /var/sites/thirdauth/static/images/companies/Stovekraft\ Private\ Limited\(mohsin\)/idea/test/ cola123.svm jpg"
        print svm_path
        print settings.MEDIA_ROOT+"/"+train_path+"/"
        faces_folder = settings.MEDIA_ROOT+"/"+train_path+"/"
        test_folder = settings.MEDIA_ROOT+"/"+test_path+"/"
        print faces_folder
        #dest = "/var/sites/thirdauth/static/images/companies/Stovekraft Private Limited(mohsin)/Docomo/svm"
        timestr = svm+time.strftime("_%m_%d_%H_%M")+".svm"
        print timestr
        outputpath = str(svm)+".svm"
        cval = cval
        options = dlib.simple_object_detector_training_options()
        options.add_left_right_image_flips = True
        options.C = int(cval)
        options.num_threads = 4
        options.be_verbose = True
        training_xml_path = os.path.join(str(faces_folder), "training.xml")
        testing_xml_path = os.path.join(str(test_folder), "training.xml")
        dlib.train_simple_object_detector(training_xml_path,outputpath, options)
        print("")
        print("Training accuracy: {}".format(
        dlib.test_simple_object_detector(training_xml_path, outputpath)))
        print("Testing accuracy: {}".format(
        dlib.test_simple_object_detector(testing_xml_path, outputpath)))
        result = "Training accuracy: {}"+format(dlib.test_simple_object_detector(training_xml_path, outputpath))+"  Testing accuracy: {}"+format(dlib.test_simple_object_detector(testing_xml_path, outputpath))
        os.rename(str(outputpath),timestr)
        if os.path.exists(str(svm_path)+"/"+str(timestr)):
             os.remove(str(svm_path)+"/"+str(timestr))
        shutil.move("/var/sites/thirdauth/"+str(timestr),str(svm_path))
        Svms(svm_name = str(timestr), brand_id = pk , company_id = brand.company_id ).save()
        return HttpResponse(result)
     else:
        return render(request,template_name, data ,context_instance=RequestContext(request))


def upload( request, pk ):
    if request.method == 'POST':
        name = request.POST.get('train')
        print name
        #brand = get_object_or_404(Brands, pk=pk)
        paths = Paths.objects.filter(brand_id = pk)
        if paths.exists():
            for pt in paths:
                if request.POST.get('train'):
                    path = pt.train_path
                if request.POST.get('test'):
                    path = pt.test_path
                if request.POST.get('demo'):
                    path = pt.demo_path
                path = pt.company_path
                if not os.path.exists(path):
                    os.makedirs(path)
        else:
            test = "/var/sites/thirdauth/static/images/default/test"
            train = "/var/sites/thirdauth/static/images/default/train"
            demo = "/var/sites/thirdauth/static/images/default/demo"
        print path
        for afile in request.FILES.getlist('docfile'):
                #Document(docfile = afile ).save()
                dest = path.split('/')
                dest = dest.pop()
                pathtosave = path+"/%s" % afile
                destination = open(pathtosave, 'wb+')
                for chunk in afile.chunks():
                    destination.write(chunk)
                    destination.close()
                baseName = os.path.basename( pathtosave )
                fileName = baseName.split('.')
                if dest == "demo":
                    if baseName.endswith(('.png', '.PNG')):
                        im = Image.open( str( pathtosave ) )
                        os.remove( str( pathtosave ) )
                        im.save( path + "/" + fileName[ 0 ] +'.jpg' )
        messages.add_message(request, messages.INFO, 'Success.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        return render(request,template_name,{'form': form,'brands':brand},context_instance=RequestContext(request))
        return HttpResponseRedirect(reverse('myapp.views.upload_img'))
    else:
        form = DocumentForm()
        documents = Document.objects.all()
        brand = get_object_or_404(Brands, pk=pk)
        return render(
            request,
            {'documents': documents, 'form': form},
            context_instance=RequestContext(request)
        )

def logout(request):
    if 'user' in request.session:
        del request.session['user']
        del request.session['role_id']
    return redirect('/')

def api(request, template_name = "image_api.html"):
    data = {}
    paths = Paths.objects.filter(id = 1)
    if paths.exists():
        for pt in paths:
            path = pt.train_path
    data[ 'file_name' ] = os.listdir(path)
    data[ 'path' ] = path
    return render(request,template_name,data)


@csrf_exempt
def image_api(request):
    if request.method == "POST":
        postDatum = request.POST.keys()
        data = []
        print postDatum
        for postData in postDatum:
            url = request.POST[postData]
            if (url.lower()).endswith(('jpg','jpeg')):
                urllib.urlretrieve(url, "static/test/abc.jpg")
            elif (url.lower()).endswith(('.png')):
                urllib.urlretrieve(url, "static/test/abc.png")
                im = Image.open("static/test/abc.png")
                im.save("static/test/abc.jpg")
                os.remove("static/test/abc.png")
            else:
                continue
            brand = request.POST['brand']
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
            img_count = []
            img_tags_count = []
            img_name = { }
            img_tags = { }
            t5tags = [ ]
            t5out = [ ]
            for f in glob.glob(os.path.join(test_folder,"abc.jpg")):
                print("Processing file: {}".format(f))
                img = io.imread(f)
                dets = detector(img)
                print("Number of Objects detected: {}".format(len(dets)))
                for k, d in enumerate(dets):
                    print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(k, d.left(), d.top(), d.right(), d.bottom()))
                    img_tags = { 'left': format(d.left()),'top': format(d.top()),'right': format(d.right()),'bottom': format(d.bottom()),'count': format(len(dets)) }
                    img_tags_count.append(img_tags)
                    h = abs( int( format(d.top()) ) - int( format(d.bottom()) ) )
                    w = abs( int( format(d.right()) ) - int( format(d.left()) ) )
                    t5tags = [ int( format(d.top()) ), int( format(d.left()) ), w , h ]
                    t5out.append( t5tags )
                img_name = { 'count':format(len(dets)), 'name':name ,'tags': img_tags_count }
                img_count.append(img_name)
                data.append(img_count)
                t5out = json.dumps( t5out )
                print t5out
                T5hawktags( picture = name, tag_count = format( len( dets ) ), tags = t5out, brandName = brand, imageType = 'activitypictures', attribute = ' ' ).save()
                os.remove("static/test/abc.jpg")
        return HttpResponse(json.dumps(data))
    else:
        return render(request,template_name, context_instance=RequestContext(request))

def listing( request, template_name = 'pagination.html' ):
    contact_list = Tags.objects.all()
    paginator = Paginator(contact_list, 25) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)

    return render( request, template_name , {"contacts": contacts})

def fetch_images( request, pk, op ):
    paths = Paths.objects.filter( brand_id = pk )
    if paths.exists():
        for pt in paths:
            if str(op) == "train":
                path = pt.train_path
            elif str(op) == "test":
                path = pt.test_path
            elif str(op) == "demo":
                path = pt.demo_path
    data = {}
    file_list = []
    files = os.listdir( path )
    for fil in files:
        if fil.endswith(('.jpg', '.jpeg','.JPG','.JPEG')):
            file_list.append( fil )
    path = os.path.relpath(path, settings.MEDIA_ROOT)
    data[ 'file_list' ] = { "/"+path+"/" : file_list}
    return HttpResponse(json.dumps(data))

@csrf_exempt
def ajupload(request):
  op = request.POST.get('op')
  # if str( op ) == 'train':
  # elif str( op ) == 'test':
  # elif str( op ) == 'demo':
  f = request.FILES.getlist('file_upload')
  for afile in f:
      path = "/var/sites/thirdauth/static/test/%s" % afile
      destination = open(path, 'wb+')
      for chunk in afile.chunks():
          destination.write(chunk)
          destination.close()
  data = "save"
  return HttpResponse(json.dumps(data))

def s3download( request, pk, op ):
    if request.method == 'POST':
        paths = Paths.objects.filter( brand_id = pk )
        if paths.exists():
            for pt in paths:
                if str( op ) == 'train':
                    path = pt.train_path
                elif str( op ) == 'test':
                    path = pt.test_path
                elif str( op ) == 'demo':
                    path = pt.demo_path
                path = pt.company_path
        data = request.POST['image']
        data = json.loads(data)
        url = data[ 'image' ]
        imageName = data[ 'imageName' ]
        count = data[ 'count' ]
        i = data[ 'ival' ]
        leftCount = int(count) - int(i)
        messages = leftCount
        storePath = path +"/"+ imageName
        if not os.path.isfile( str( storePath) ):
            attempts = 0
            while attempts <= 3:
                timeout = 30
                socket.setdefaulttimeout(timeout)
                try:
                    urllib.urlretrieve( url , str( storePath ) )
                    print "try"
                    if os.path.isfile( storePath ):
                        print "m here"
                        attempts = 4
                except:
                    attempts += 1
                    print "except"
        if str( op ) == 'demo':
            imgName = imageName.split('.')
            print imgName[0]
            im = Image.open( str( storePath ) )
            Save = str(path) + "/" + str(imgName[0]) +'.jpg'
            print Save
            im.save( str(Save) )
            os.remove( str( storePath ) )
        # message = str(left)+" off"+str(count)+"completed"
        # im = Image.open( str( storePath ) )
        # os.remove( str( storePath ) )
        # im.save( path + "/" + imgName[ 0 ] +'.jpg' )
        # print "hello"
        # paths = Paths.objects.filter( brand_id = pk )
        # if paths.exists():
        #     for pt in paths:
        #         if str( op ) == 'train':
        #             path = pt.train_path
        #         elif str( op ) == 'test':
        #             path = pt.test_path
        #         elif str( op ) == 'demo':
        #             path = pt.demo_path
        # data = request.POST['image']
        # data = json.loads(data)
        # print data['todate']
        # #http://stagingvadilal.bizom.in/activities/getPictures?&fromdate=2015-01-01&todate=2016-01-01&tableName=activitypictures
        # mid = "http://stagingvadilal.bizom.in/activities/getPictures?&fromdate="+data[ 'fromdate' ]+"&todate="+data[ 'todate' ]+"&pageno=1&limit=30&tableName="+data[ 'tableName' ]
        # req = urllib2.Request (mid)
        # req.add_header('Accept', mid)
        # resp = urllib2.urlopen(req)
        # content = resp.read()
        # Data = json.loads(content)
        # print path
        # imageUrl = Data[ 'data' ][ 'bucket' ]
        # images = Data[ 'data' ][ 'pictures' ]
        # for image in images:
        #     print image
        #     imgName = image.split( '.' )
        #     url = imageUrl+image
        #     print url
        #     storePath = path +"/"+ image
        #     print storePath
        #     time.sleep( 5 )
        #     urllib.urlretrieve( str( url ), str( storePath ) )
            # im = Image.open( str( storePath ) )
            # os.remove( str( storePath ) )
            # im.save( path + "/" + imgName[ 0 ] +'.jpg' )
        return HttpResponse(json.dumps(messages))
    return HttpResponse(json.dumps('Error'))

def HawkTags( request ):
    companies = Companies.objects.filter( id = 3 )
    if companies.exists():
        for company in companies:
            domainName = company.domainname
    print domainName
    fromdate = '2014-07-01'
    todate = '2014-09-01'
    tableName = 'activitypicture'
    brands_id = 1
    url = "http://stagingadpl.bizom.in/activities/getPictures?&fromdate=2014-07-01&todate=2014-09-01&pageno=6&limit=10&tableName=activitypictures"
    req = urllib2.Request ( url )
    req.add_header('Accept', url )
    resp = urllib2.urlopen( req )
    content = resp.read()
    content = json.loads( content )
    print content
    error = content[ 'result' ]
    if error != True:
        return HttpResponse( "No data found for this date range.." )
    data = []
    attributes = { }
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
        picName = imgName[0]+".jpg"
        while attempts <= 3:
            timeout = 30
            socket.setdefaulttimeout(timeout)
            try:
                if not os.path.isfile( "static/test/"+imgName[0]+".jpg" ):
                    if (url.lower()).endswith(('.png')):
                        urllib.urlretrieve(url, "static/test/"+img_name)
                        im = Image.open("static/test/"+img_name)
                        im.save("static/test/"+imgName[0]+".jpg")
                        os.remove("static/test/"+img_name)
                    else:
                        continue
                print "try"
                if os.path.isfile( "static/test/"+imgName[0]+".jpg" ):
                    print "m here"
                    attempts = 4
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
            #os.remove("static/test/abc.jpg")
    return HttpResponse(json.dumps(data))

def HawkFetchTags( request ):
    try:
        url = "http://stagingadpl.bizom.in/activities/getPictures?&fromdate=2014-07-01&todate=2014-09-01&pageno=6&limit=10&tableName=activitypictures"
        req = urllib2.Request ( url )
        req.add_header('Accept', url )
        resp = urllib2.urlopen( req )
        content = resp.read()
        content = json.loads( content )
    except:
        return HttpResponse("Internet connection too slow..!!")
    datas = content[ 'data' ][ 'pictures' ]
    HawkTags = { }
    attributes = { }
    Hawk = []
    for data in datas:
        tagdatas = T5hawktags.objects.filter( picture = data[ 'img_name' ], t5hawkbrand_id = 1 )
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
    return HttpResponse(json.dumps(Hawk))

@never_cache
def commondownload( request, pk ,template_name='myapp/commanDownload.html'):
    paths = Paths.objects.filter( brand_id = pk )
    if paths.exists():
        for path in paths:
            filePath = path.company_path
            companyId = path.company_id
    data = { }
    fileList = [ ]
    filePath = filePath
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    for file in os.listdir( filePath ):
        if file.endswith( ('.jpg', '.JPG', '.jpeg', 'JPEG', '.png', '.PNG') ):
            fileList.append( file )
    data[ 'file_name' ] = fileList
    path = os.path.relpath(filePath, settings.MEDIA_ROOT)
    data[ 'path' ] = "/"+str(path)+"/"
    data[ 'file_path' ] = settings.MEDIA_ROOT+"/"+path+"/"
    data[ 'brand_id' ] = pk
    data[ 'cid' ] = companyId
    return render( request, template_name, data )

def copyImage( request, pk, op ):
     if request.method == 'POST':
        paths = Paths.objects.filter( brand_id = pk )
        if paths.exists():
            for pt in paths:
                if str( op ) == 'train':
                    path = pt.train_path
                elif str( op ) == 'test':
                    path = pt.test_path
                elif str( op ) == 'demo':
                    path = pt.demo_path
                sorcePath = pt.company_path
        data = request.POST['image']
        data = json.loads(data)
        imageName = data[ 'imageName' ]
        count = data[ 'count' ]
        i = data[ 'ival' ]
        leftCount = int(count) - int(i)
        messages = leftCount
        sorcePath = sorcePath +"/"+ imageName
        if str( op ) == 'delete':
            os.remove( sorcePath )
            return HttpResponse( json.dumps("deleted") )
        storePath = path +"/"+ imageName
        imgName = imageName.split('.')
        if not os.path.isfile( storePath ):
            shutil.copy2( str( sorcePath ), str( storePath ) )
        if str( op ) == 'demo':
            im = Image.open( storePath )
            im.save( path+'/'+imgName[0]+".jpg")
        return HttpResponse( json.dumps( messages ) ) 
        
















