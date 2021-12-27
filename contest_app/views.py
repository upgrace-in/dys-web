
from django.core import serializers
from django.db.models.query import QuerySet
from django.http.response import Http404
from django.shortcuts import redirect, render, HttpResponse
from django.views.decorators import csrf
import razorpay
import random
import json
import os
from django.forms.models import model_to_dict
import uuid
from contest_app import models
from django.views.decorators.csrf import csrf_exempt
import smtplib
from email import encoders
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from threading import Thread
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
path = os.path.abspath('.')
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    path+'/static/creds.json', scope)

live = "rzp_live_LykfrqrRQz1DIi"
secret = "sRobucivMXuz4rxuia3KzIXX"
test = "rzp_test_IyvQ5bI5rXkMyT"
test_secret = "Xt3HNwMnjP3hlAEUMHiTsMjK"

def send_mail(receiver_address, name, id):
    mail_content = '<div style="font-size: 1.2rem">Hi <b>{name}</b>,<Br><Br>Thank you for your registration.<br><Br>Your unique ID : <b><Br>{id}</b><Br><Br>Best regards,<br><b>Our Team</b><Br><Br>'.format(
        name=name, id=id)

    sender_address = 'upgrace.in@gmail.com'
    sender_pass = '(Hari@47)'
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'DYS - Registration Successful'
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'html'))

    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    # login with mail_id and password
    session.login(sender_address, sender_pass)
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')

def sheet_updation(hash, name, age, mail_id, phone_num, lang, occupation, qualification, order_id):
    client = gspread.authorize(credentials)
    sheet = client.open("online").sheet1
    sheet.append_row([hash, name, age, mail_id, phone_num, lang, occupation, qualification, order_id])
    print("Sheet Updated")

@csrf_exempt
def verify_payment(request):
    try:
        razorpay_order_id = request.POST['razorpay_order_id']
        razorpay_payment_id = request.POST['razorpay_payment_id']
        razorpay_signature = request.POST['razorpay_signature']

        client = razorpay.Client(
            auth=(live, secret))

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        c = client.utility.verify_payment_signature(params_dict)
        if c is None:

            mdl = models.users_data.objects.create(id=str(uuid.uuid1()).replace('-', ''),
                                                   name=request.POST['name'], age=request.POST['age'], mail_id=request.POST['mail_id'], phone_num=request.POST[
                'phone_num'], occupation=request.POST['occupation'], qualification=request.POST['qualifications'], lang=request.POST['lang'], razorpay_order_id=razorpay_order_id,
                razorpay_payment_id=razorpay_payment_id, razorpay_signature=razorpay_signature)

            thread = Thread(target=send_mail, args=(
                request.POST['mail_id'], request.POST['name'], mdl.id))
            thread.start()

            thread1 = Thread(target=sheet_updation, args=(mdl.id, request.POST['name'], request.POST['age'], request.POST['mail_id'],
                                                          request.POST['phone_num'], request.POST['lang'], request.POST['occupation'], request.POST['qualifications'], razorpay_order_id))
            thread1.start()

            context = {
                'result': 'success',
                'id': mdl.id
            }
        else:
            context = {
                'result': 'verify_failed'
            }
    except Exception as e:
        print(e)
        context = {
            'result': 'error'
        }
    data = json.dumps(context, indent=4, sort_keys=True, default=str)
    return HttpResponse(data, content_type='application/json')


def create_an_order(request):
    if request.method == 'POST':
        fees = 50
        client = razorpay.Client(
            auth=(live, secret))

        order_currency = 'INR'
        order_receipt = 'ord_rcpt'+str(random.randint(0, 100000))
        c = client.order.create(dict(amount=int(str(fees)+"00"),
                                currency=order_currency, receipt=order_receipt))
        context = {
            'order': c
        }
        data = json.dumps(context, indent=4, sort_keys=True, default=str)
        return HttpResponse(data, content_type='application/json')
    else:
        return HttpResponse("Method Not Allowed")