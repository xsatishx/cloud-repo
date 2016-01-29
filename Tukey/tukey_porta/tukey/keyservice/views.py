from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from tukey.keyservice.models import Key, Repository
from tukey.keyservice.forms import ARKForm, RepositoryForm, KeyForm,MetadataForm
import re,json,datetime
import smtplib
from django.core.mail import EmailMessage
import settings
from django.shortcuts import render
from signpostclient import SignpostClient
from psqlgraph import PsqlGraphDriver
from settings import SIGNPOST_URL, METADATA_DB
#For now going to assume the prefix are letters and the id is digits... can change later?
#In a lot of ways this is a hack -- needs to play better with the datasets in general.

client = SignpostClient(SIGNPOST_URL,version='v0')
pg_driver = PsqlGraphDriver(METADATA_DB['HOST'],METADATA_DB['USER'],
        METADATA_DB['PASSWORD'],METADATA_DB['NAME']) 

def keyservice_invalid(request, key):
    print('invalid response')
    return render_to_response('keyservice/invalid.html', {'key' : key}, context_instance=RequestContext(request))

def keyservice(request):
    if request.method == 'POST':
        form = ARKForm(request.POST)
        if form.is_valid():
            ark_key = form.cleaned_data['ark_key']
            url = '/keyservice/' + ark_key
            if ark_key.endswith("?"):
                url = url[0:-1]+"/metadata"
            return HttpResponseRedirect(url)
    else:
        form = ARKForm()

    return render_to_response('keyservice/keyservice_index.html', {'form' : form }, context_instance=RequestContext(request))

meta_keys = ['title','investigator_name','investigator_affiliation','size','description','date_collected','date_uploaded','date_updated','keywords','availability_type','availability_mechanism',
        'grant_or_support_source_and_id','acknowledgements','publications','slug','identifiers','access_point']
def keyservice_meta(request,key):
    match = match_key(key)
    if match:
        (identify_method,subkey) = match
        try:
            doc = client.search(identify_method+':'+subkey)
            with pg_driver.session_scope():
                node = pg_driver.nodes().ids(doc.did).first()
                result = ''
                for key in meta_keys:
                    if key == 'keywords':
                        result +='Keywords: '
                        for edge in node.edges_out:
                            result += edge.dst['value']+", "
                        result =result[0:-2]+"<br>"
                    elif key == 'identifiers':
                        result +='Identifiers: '
                        for identify_method,code in doc.identifiers.iteritems():
                            result+=identify_method+':' + code+" "
                        result+="<br>"
                    else: 
                        if key in node.properties:
                            value=node[key]
                            result += (" ".join(key.split("_"))).title()
                            result += ": "+value+"<br>"
                return HttpResponse(result)
        except:
            return render_to_response('keyservice/does_not_exist.html', {'key' : key}, context_instance=RequestContext(request))


def match_key(key):
    match = re.search(r'^(\w+):/(\d+)/', key)
    print key
    if match:
        identify_method = match.group(1)
        naan = match.group(2)
        if naan == "31807":
            subkey = key[match.end(2)+1:]
            return identify_method,'/'+naan+'/'+subkey
    return None

def keyservice_request(request):
    if request.method == 'POST':
        form = MetadataForm(request.POST)
        if form.is_valid():
            message_admin = build_message(form)
            subject = '%s OSDC metadata service request' % form.cleaned_data['email']
            sender_admin = form.cleaned_data['email']
            recipients_admin = [settings.APPLICATION_EMAIL]

            # Values for confirmation email to user ('Subject' remains same)
            message_user = (
                    "Thank you for your application to the OSDC. "
                    "Someone from our team will contact you within "
                    "one business day.\n\n%s" % message_admin)

            sender_user = 'noreply@opensciencedatacloud.org'
            recipients_user = [sender_admin]

            email_admin = EmailMessage(subject, message_admin, sender_admin, recipients_admin)
            email_user = EmailMessage(subject, message_user, sender_user, recipients_user)
            email_user.attach('metadata.json',json.dumps(form.cleaned_data))
            try:
                email_admin.send()
                email_user.send()
                return render(request,'webforms/apply_thanks.html')

            except smtplib.SMTPRecipientsRefused as e:
                form._errors["email"] = ErrorList(
                    # Changed 'sender' to 'sender_admin' after code split into two emails.
                    [u"Domain of address %s does not exist" % sender_admin])


    else: 
        form = MetadataForm()
    return render(request, 'keyservice/keyservice_request.html',{
        'form':form,
    })
    
         
def build_message(form):
    msg_list=''
    for key in form.fields:
        value = form.cleaned_data[key]
        if type(value) == datetime.date:
            form.cleaned_data[key]=str(value)
        msg_list+=key+':\n'+str(value)+'\n'
    return msg_list



def keyservice_lookup(request, key):
    match = match_key(key)
    print key
    if match:
        (identify_method,subkey)=match
        print subkey
        try:        
            doc = client.search(identify_method+":"+subkey)
            if len(doc.urls)>0:
                return HttpResponseRedirect(doc.urls[0])
            else:
                return render_to_response('keyservice/does_not_exist.html', {'key' : key}, context_instance=RequestContext(request))
        except Exception as e:
            print str(e)
            return render_to_response('keyservice/does_not_exist.html', {'key' : key}, context_instance=RequestContext(request))
                
                
            #return HttpResponse("We are the naan and the key is: " + key + " prefix is: " + prefix + " id is: " + key_id + " from db: " + url)
        else:
            return render_to_response('keyservice/invalid_naan.html', {'naan' : naan}, context_instance=RequestContext(request))

    return render_to_response('keyservice/invalid.html', {'key' : key}, context_instance=RequestContext(request))
    

def add_repository(request):
    if request.user.is_authenticated():
        f = RepositoryForm(request.POST or None)
        if f.is_valid():
            f.save()
            f = RepositoryForm()
            return render_to_response("keyservice/repository_add.html", {'form': f, 'success' : 'Repository Saved'}, context_instance=RequestContext(request))

        return render_to_response("keyservice/repository_add.html", {'form': f}, context_instance=RequestContext(request))
    return redirect("keyservice:keyservice_index")

def add_key(request):
    if request.user.is_authenticated():
        f = KeyForm(request.POST or None)
        if f.is_valid():
            f.save()
            f = KeyForm()
            return render_to_response("keyservice/key_add.html", {'form': f, 'success' : True}, context_instance=RequestContext(request))

        return render_to_response("keyservice/key_add.html", {'form': f}, context_instance=RequestContext(request))
    return redirect("keyservice:keyservice_index")
