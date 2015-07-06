
from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
	url(r'^$', views.check),
	url(r'^Home', views.company_list, name = 'company_list' ),
	url(r'^brand/(?P<pk>\d+)',views.brand_list,name = 'brand_list' ),
	url(r'^new/(?P<pk>\d+)', views.brand_create, name = 'brand_new' ),
    url(r'^cnew', views.company_create, name = 'company_new' ),
	url(r'^edit/(?P<pk>\d+)$', views.brand_update, name = 'brand_edit' ),
	url(r'^delete/(?P<pk>\d+)', views.brand_delete, name = 'brand_delete' ),
	url(r'^select/(?P<pk>\d+)/(?P<op>\w+)',views.select_image,name = 'select_image' ),
	#url(r'^upload/(?P<pk>\d+)', views.upload_img, name='upload_img'),
    url(r'^upload/(?P<pk>\d+)', views.upload, name = 'upload' ),
    url(r'^ajax/(?P<pk>\d+)/(?P<op>\w+)', views.ajax, name = 'ajax' ),
    url(r'^operate', views.operation, name = 'operate' ),
    url(r'^result/(?P<pk>\d+)/(?P<svm>\w+)', views.result, name = 'result' ),
    url(r'^demo/(?P<pk>\d+)', views.demo, name = 'demo' ),
    url(r'^api', views.api, name = 'api' ),
    url(r'^image_api', views.image_api, name = 'image_api' ),
    url(r'^create/(?P<pk>\d+)', views.create_svm, name = 'create_svm' ),
    url(r'^listing', views.listing, name = 'listing' ),
    url(r'^fetch/(?P<pk>\d+)/(?P<op>\w+)', views.fetch_images, name = 'fetch_images' ),
	url(r'^ajupload', views.ajupload, name = 'ajupload' ),
	url(r'^s3download/(?P<pk>\d+)/(?P<op>\w+)', views.s3download, name = 's3download' ),
	url(r'^HawkTags', views.HawkTags, name = 'HawkTags' ),
    url(r'^HawkFetchTags', views.HawkFetchTags, name = 'HawkFetchTags' ),
    url(r'^commondownload/(?P<pk>\d+)', views.commondownload, name = 'commondownload' ),
    url(r'^copyImage/(?P<pk>\d+)/(?P<op>\w+)', views.copyImage, name = 'copyImage' ),
    url(r'^logout', views.logout, name='logout'),

)
