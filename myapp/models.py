# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [app_label]'
# into your database.

from __future__ import unicode_literals
from django.db import models
from django.core.urlresolvers import reverse


class Brands(models.Model):
    name = models.CharField(max_length=50)
    colorname = models.CharField(max_length=20)
    colorval = models.CharField(max_length=7)
    heatmapcolor = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)
    company_id = models.IntegerField()
    isactive = models.IntegerField()
    class Meta:
        managed = True
        db_table = 'brands'

def __str__(self):
        return self.name


class Buckets(models.Model):
    url = models.CharField(max_length=255)
    name = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'buckets'


class Companies(models.Model):
    name = models.CharField(max_length=255)
    erp_id = models.IntegerField()
    domainname = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'companies'

def __str__(self):
        return self.name

def __str__(self):
        return self.erp_id

class Picturetypes(models.Model):
    name = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)
    isactive = models.IntegerField()
    company_id = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'imagetypes'

def __str__(self):
        return self.name

class Paths(models.Model):
    train_path = models.CharField(max_length=255)
    test_path = models.CharField(max_length=255)
    demo_path = models.CharField(max_length=255)
    company_path = models.CharField(max_length=255,default='')
    svm_path = models.CharField(max_length=255,default='')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)
    brand_id = models.IntegerField()
    company_id = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'paths'

def __str__(self):
        return '%s %s %s %s' % (self.train_path, self.test_path,self.demo_path,svm_name)


class Pictures(models.Model):
    picture_name = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)
    company_id = models.IntegerField()
    bucket_id = models.IntegerField()
    picturetable_id = models.IntegerField()
    imagetype_id = models.IntegerField()
    brand_id = models.IntegerField()
    company_id = models.IntegerField()
    class Meta:
        managed = True
        db_table = 'pictures'


class Picturetables(models.Model):
    tablename = models.CharField(max_length=50)
    jsonpath = models.CharField(max_length=20)
    fetchstartdate = models.DateTimeField()
    fetchenddate = models.DateTimeField()
    fetchtime = models.DateTimeField()
    isactive = models.IntegerField( default = 0 )
    brand_id = models.IntegerField()
    company_id = models.IntegerField()
    status = models.IntegerField( default = 0 )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        managed = True
        db_table = 'picturetables'

def __str__(self):
        return self.tablename


class Tags(models.Model):
    top = models.IntegerField()
    left = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)
    picture_id = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'tags'


class Users(models.Model):
	name = models.CharField(max_length=50)
	company_id = models.IntegerField()
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now_add=True)

def __unicode__(self):
        return self.name

def __str__(self):
        return self.name

def get_absolute_url(self):
        return reverse('company_edit', kwargs={'pk': self.pk})

class Document(models.Model):
    docfile = models.FileField(upload_to='train')

class Svms(models.Model):
    svm_name = models.CharField(max_length = 50)
    brand_id = models.IntegerField()
    company_id = models.IntegerField()
    isdefault = models.IntegerField( default = 0 )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)

class T5hawktags( models.Model ):
    picture = models.CharField( max_length = 100 )
    tag_count = models.IntegerField()
    tags = models.CharField( max_length = 1000 )
    brandName = models.CharField( max_length = 30, default='' )
    attribute = models.CharField( max_length = 2000, default='' )
    t5hawkbrand_id = models.IntegerField( default = 0 )
    created = models.DateTimeField( auto_now_add = True )
    modified = models.DateTimeField( auto_now_add = True )
    
class crons( models.Model ):
    cronName = models.CharField( max_length = 20 )
    domainName = models.CharField( max_length = 20 )
    tablename = models.CharField( max_length = 100 )
    svmnames = models.CharField( max_length = 100)
    fetchstartdate = models.DateTimeField( auto_now_add=True )
    fetchenddate = models.DateTimeField( auto_now_add=True )
    fetchtime = models.DateTimeField( auto_now_add=True, default='2015-01-01' )
    isactive = models.IntegerField()
    status = models.IntegerField()
    
