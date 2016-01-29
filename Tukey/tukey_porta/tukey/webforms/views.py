import smtplib

from django.conf import settings
from django.contrib.auth import logout
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.mail import send_mail, BadHeaderError
from django.core.validators import validate_email
from django.forms.util import ErrorList
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django_openid_auth.views import parse_openid_response
from openid.consumer.consumer import SUCCESS
from tukey.openid_auth import pre_apply
from tukey.webforms.forms import OSDCForm, OSDCSupportForm, OSDCDemoForm

def build_message(form):
    msg_list = []
    msg_list.append('Summary of submitted information:\n\n')
    msg_list.append('From:\n')
    msg_list.append(form.cleaned_data['first_name'])
    msg_list.append(' ')
    msg_list.append(form.cleaned_data['last_name'])
    msg_list.append('\n')
    msg_list.append(form.cleaned_data['email'])
    msg_list.append('\nIdentifier:\n')
    msg_list.append(form.cleaned_data['eppn'])
    msg_list.append('\nMethod:\n')
    msg_list.append(form.cleaned_data['method'])
    msg_list.append('\nOrganization/University:\n')
    msg_list.append(form.cleaned_data['organization'])
    msg_list.append('\n\nStatus:\n')
    msg_list.append(form.cleaned_data['status'])
    msg_list.append('\n\nResearch fields:\n')
    for item in form.cleaned_data['researchs']:
	if item == 'physical-sciences':
	    msg_list.append('Physical Sciences (physics, chemistry, astronomy)\n')
	elif item == 'earch-and-environmental-sciences':
	    msg_list.append('earch-and-environmental-sciences\n')
	elif item == 'biological-sciences':
	    msg_list.append('Biological Sciences\n')
	elif item == 'social-sciences':
	    msg_list.append('Social Sciences\n')
	elif item == 'urban-sciences':
	    msg_list.append('Urban Sciences\n')
	elif item == 'computer-science-and-mathematics':
	    msg_list.append('Computer Science and Mathematics\n')
	elif item == 'medical-and-health-related':
	    msg_list.append('Medical and Health related\n')
	elif item == 'digital-humanities':
	    msg_list.append('Digital Humanities\n')
	elif item == 'other':
	    msg_list.append('Other\n')
	      
    if form.cleaned_data['webpage'] != '':
        msg_list.append('\n\nWeb page:\n')
        msg_list.append(form.cleaned_data['webpage'])
    if form.cleaned_data['phonenumber'] != '':
        msg_list.append('\n\nPhone number:\n')
        msg_list.append(form.cleaned_data['phonenumber'])
    if form.cleaned_data['address'] != '':
        msg_list.append('\n\nAddress:\n')
        msg_list.append(form.cleaned_data['address'])

    msg_list.append('\n\nAccess Requested:\n')
    for item in form.cleaned_data['systems']:
        if item == 'OSDC-Sullivan':
            msg_list.append('General Compute Cloud\n')
        elif item == 'OSDC-Adler':
            msg_list.append('OSDC-Adler\n')
        elif item == 'OSDC-Atwood':
            msg_list.append('Protected Compute Cloud\n')
        elif item == 'OSDC-Skidmore':
            msg_list.append('OSDC-Skidmore\n')
        elif item == 'occ-y':
            msg_list.append('Hadoop Cluster\n')
        elif item == 'bionimbus_cc':
            msg_list.append('Bionimbus Community Cloud\n')
        elif item == 'bionimbus_uchicago':
            msg_list.append('UChicago Bionimbus Cloud\n')
        elif item == 'matsu':
            msg_list.append('Matsu Testbed\n')

        






    msg_list.append('\n\nProject Name:\n')
    msg_list.append(form.cleaned_data['projectname'])
    msg_list.append('\n\nProject Description\n')
    msg_list.append(form.cleaned_data['projectdescr'])

    if (form.cleaned_data['sharing'] != ""):
        msg_list.append('\n\nSharing with:\n')
        msg_list.append(form.cleaned_data['sharing'])

    msg_list.append('\n\nProject Lead\n')
    msg_list.append(form.cleaned_data['projectlead'])
    msg_list.append('\n\nProject Lead E-mail:\n')
    msg_list.append(form.cleaned_data['projectlead_email'])
    msg_list.append('\n\nEstimated CPUs:\n')
    msg_list.append(form.cleaned_data['cpus'])

    if form.cleaned_data['more_cpus'] != "":
        msg_list.append("(Specific requirements: " + form.cleaned_data['more_cpus'] + ")")

    msg_list.append('\n\nEstimated storage:\n')
    msg_list.append(form.cleaned_data['storage'])

    if form.cleaned_data['more_storage'] != "":
        msg_list.append("(Specific requirements: " + form.cleaned_data['more_storage'] + ")")

    msg_list.append('\n\nInformation about how data intensive the project is:\n')
    msg_list.append(form.cleaned_data['datadescr'])
    msg_list.append('\n\n')
    
    msg_list.append('\n\nHeard about OSDC from:\n')
    msg_list.append(form.cleaned_data['referral_source'])
    msg_list.append('\n\n')
    
    #agreement
    msg_list.append('\nIf my request for an OSDC resource allocation is approved, I agree to:\n\n')
    msg_list.append('    - Make appropriate use of OSDC resources and use good social behavior (ie - terminating VMs when not in use).\n')
    msg_list.append('    - Do not share ssh keys or login information - One user per resource allocation.\n')
    msg_list.append('    - Cite the OSDC in any papers and publications.\n')
    msg_list.append('    - Regularly respond to quarterly OSDC allocation surveys.\n')
    msg_list.append('    - Submit tickets to the OSDC support ticketing system when encountering technical issues not covered by the OSDC support documentation.\n\n')	 
    
    return ''.join(msg_list)

def osdc_apply(request, user=None):
    if user is None:
        user = request.user

    if request.method == 'POST': # If the form has been submitted...
        form = OSDCForm(request.POST, request.FILES) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            subject = '%s %s OSDC Account Request' % (form.cleaned_data['first_name'],
                    form.cleaned_data['last_name'])
            message_admin = build_message(form)
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

            if "pubkey" in request.FILES:
                pubkey = request.FILES["pubkey"]
                email_admin.attach(pubkey.name, pubkey.read(), pubkey.content_type)
                email_user.attach(pubkey.name, pubkey.read(), pubkey.content_type)

            try:
                email_admin.send()
                email_user.send()
                if not request.user.is_authenticated():
                    logout(request)
                    # Redirect after POST
                return HttpResponseRedirect('thanks/')

            except smtplib.SMTPRecipientsRefused as e:
                form._errors["email"] = ErrorList(
                    # Changed 'sender' to 'sender_admin' after code split into two emails.
                    [u"Domain of address %s does not exist" % sender_admin])

    else:
        if request.user.is_authenticated():
            form = OSDCForm(initial={"eppn": user.username,
                    "method": "re-apply"})
        elif hasattr(user, 'identifier'):
            try:
                email_value = user.identifier
                validate_email(email_value)
            except ValidationError:
                email_value = ""

            form = OSDCForm(initial={"eppn": user.identifier,
                    "email": email_value, "method": user.method})
        else:
            return HttpResponseRedirect('/pre_apply/?next=/apply/')

    return render(request, 'webforms/osdc_apply.html', {
        'form': form,
    })

def osdc_apply_thanks(request):
    return render(request, 'webforms/apply_thanks.html')

def support(request):
    if request.method == 'POST': # If the form has been submitted...
        form = OSDCSupportForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']

            recipients = [settings.SUPPORT_EMAIL]

            from django.core.mail import send_mail
            send_mail(subject, message, sender, recipients)
            return HttpResponseRedirect('thanks/') # Redirect after POST

    else:
        form = OSDCSupportForm() # An unbound form

    return render(request, 'webforms/support_form.html', {
        'form': form,
    })

def support_thanks(request):
    return render(request, 'webforms/support_thanks.html')

def osdc_demo(request):
    if request.method == 'POST': # If the form has been submitted...
        form = OSDCDemoForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            subject = "Demo Registration"# form.cleaned_data['subject']
            message = ""
            for k, v in form.cleaned_data.items():
                message += k + ": " + v + "\n"
            #message = str(form.cleaned_data)
            sender = form.cleaned_data['email']

            recipients = [settings.DEMO_REG_EMAIL]

            from django.core.mail import send_mail
            send_mail(subject, message, sender, recipients)
            return HttpResponseRedirect('thanks/') # Redirect after POST

    else:
        form = OSDCDemoForm() # An unbound form

    return render(request, 'webforms/demo_form.html', {
        'form': form,
    })


def osdc_demo_thanks(request):
    return render(request, 'webforms/demo_thanks.html', {
        'email': settings.DEMO_REG_EMAIL
    })
