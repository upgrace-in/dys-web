from django.shortcuts import HttpResponse
import json
import os
import uuid
from contest_app import models
from django.views.decorators.csrf import csrf_exempt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Thread
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
path = os.path.abspath('.')
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    path+'/static/creds.json', scope)


def sheet_updation(hash, name, age, mail_id, phone_num, lang, occupation, qualification, order_id):
    try:
        client = gspread.authorize(credentials)
        sheet = client.open("online").sheet1
        sheet.append_row([hash, name, age, mail_id, phone_num,
                        lang, occupation, qualification, order_id])
    except Exception as e:
        print(e)


@csrf_exempt
def verify_payment(request):
    try:

        mdl = models.users_data.objects.create(id=str(uuid.uuid1()).replace('-', ''),
                                               name=request.POST['name'], age=request.POST['age'], mail_id=request.POST['mail_id'], phone_num=request.POST[
            'phone_num'], occupation=request.POST['occupation'], qualification=request.POST['qualifications'], lang=request.POST['lang'], razorpay_order_id='null',
            razorpay_payment_id='null', razorpay_signature='null')

        thread1 = Thread(target=sheet_updation, args=(mdl.id, request.POST['name'], request.POST['age'], request.POST['mail_id'],
                                                      request.POST['phone_num'], request.POST['lang'], request.POST['occupation'], request.POST['qualifications'], 'None'))
        thread1.start()

        context = {
            'result': 'success',
            'id': mdl.id
        }

    except Exception as e:
        context = {
            'result': 'error'
        }
    data = json.dumps(context, indent=4, sort_keys=True, default=str)
    return HttpResponse(data, content_type='application/json')

