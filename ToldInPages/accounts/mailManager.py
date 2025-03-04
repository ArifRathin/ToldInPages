import random
from django.core.mail import EmailMultiAlternatives


def genSecurityCode(request):
    digit_list = ['1','2','3','4','5','6','7','8','9']
    security_code_list = random.choices(digit_list,k=6)
    security_code = ''.join(security_code_list)
    return security_code


def sendSecurityCode(request,security_code,subj):
    mail_from = 'ecc.eagle@gmail.com'
    mail_body = "<div style='text-align:center; display:block;'><h1>Security Code</h1></div><div style='display:block'><p>Hello.</p><p>A 6-digit security code has been generated for you. Please use it in due purpose.</p><p>Security Code:<b>"+security_code+"</b></p></div>"
    mail_to = request.POST.get('email')
    mail = EmailMultiAlternatives(subj, mail_body, mail_from, [mail_to])
    mail.content_subtype = 'html'
    mail.send()
    return True