from django.conf.urls import patterns, include, url

urlpatterns = patterns('tukey.webforms.views',
    url(r'^pre_apply/$', 'pre_apply'),
    url(r'^apply/$', 'osdc_apply'),
    url(r'^apply/thanks/', 'osdc_apply_thanks'),                   
    #url(r'^apply/invited/thanks/', 'osdc_apply_invite_thanks'),
    #url(r'^apply/invited/', 'osdc_apply_invite'),                   
    #url(r'^apply/pdc/thanks/', 'osdc_apply_pdc_thanks'),
    #url(r'^apply/pdc/', 'osdc_apply_pdc'),                   
    url(r'^support/$', 'support'),
    url(r'^support/thanks/', 'support_thanks'),
    url(r'^demoregister/$', 'osdc_demo'),
    url(r'^demoregister/thanks/', 'osdc_demo_thanks'),
    #url(r'^blank/$', 'blank')
)
