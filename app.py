from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz, json, requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gagan42-mnm-api'
scheduler = BackgroundScheduler()
scheduler.start()

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": '<api-email>'
    "MAIL_PASSWORD": '<api-email-password>'
    "MAIL_DEFAULT_SENDER": 'tester'
}

app.config.update(mail_settings)
mail = Mail(app)

tz = pytz.timezone('Asia/Kolkata')
jsonfile = open('codes.json', encoding = "utf-8")
country_codes = json.load(jsonfile)
codes = set([code['dial_code'] for code in country_codes])
jsonfile.close()

def send_message(message, req):
    
    req_params = {
        'apikey': req['apikey'],
        'secret': req['secret'],
        'usetype': 'stage',
        'phone': req['to'],
        'message': message,
        'senderid': req['from']
    }

    return requests.post('https://www.way2sms.com/api/v1/sendCampaign', req_params)
    
def send_mail(message, req):

    with app.app_context():
        msg = Message(subject= req['subject'],
                      sender = app.config.get("MAIL_DEFAULT_SENDER"),
                      recipients= req['to'],
                      body= message)
        mail.send(msg)

def scheduled(request, flag):

    x = ''
    if flag in {0, 2}:
        x = send_message(request['message'], request['sms'])
       
    if flag in {1, 2}:
        send_mail(request['message'], request['mail'])

    return 1


def validate(req, value):
    
    check = 1
    dtc = {'year', 'month', 'day', 'hour', 'minute', 'second'}
    sc = {'to', 'from', 'apikey', 'secret'}
    mc = {'to', 'from', 'subject'}
    
    if not req.get('datetime', None) or not req.get('message', None):
        check = 0
        return 'datetime or message missing'

    elif type(req['datetime']) != dict or type(req['message']) != str:
        check = 0
        return 'datetime or message type not correct'

    elif any(i not in req['datetime'].keys() or type(req['datetime'][i]) != int for i in dtc):
        check = 0
        return 'key missing in datetime'

    elif value in {'sms', 'both'}:
        if not req.get('sms', None):
            check = 0
            return 'sms not found'
            
        elif any(i not in req['sms'].keys() or type(req['sms'][i]) != str for i in sc):
            check = 0
            return 'key missing or format not correct - sms'

        elif len(req['sms']['to']) != 13 or len(req['sms']['from']) != 13:
            check = 0
            return 'wrong phone number format'

        elif req['sms']['to'][:3] not in codes or req['sms']['from'][:3] not in codes:
            check = 0
            return 'invalid country code'

    elif value in {'mail', 'both'}:
        if not req.get('mail', None):
            check = 0
            return 'mail not found'

        elif any(i not in req['mail'].keys() for i in mc):
            check = 0
            return 'key missing in mail'

        elif type(req['mail']['to']) != list:
            check = 0
            return 'to in mail should be list'

        elif any(type(i) != str for i in req['mail']['to']):
            check = 0
            return 'email id should be a string'

        elif type(req['mail']['from']) != str or type(req['mail']['subject']) != str:
            check = 0
            return 'from and subject should be string'

    return check


@app.route('/v1/<value>', methods=['POST'])
def main_send(value):

    try:
        if request.method == 'POST':
            req = request.get_json(force=True)
            dtti = datetime.now()
            flg = -1
            x = validate(req, value)
            
            if value == 'sms':
                if x!=1: pass
                else: flg = 0
                    
            elif value == 'mail':
                if x!=1: pass
                else: flg = 1
                    
            elif value == 'both':
                if x!=1: pass
                else: flg = 2

            if flg == -1:
                return jsonify(results = {'response_text': x})
            
            else:
                tm = req['datetime']
                tm = f"{tm['year']}-{tm['month']}-{tm['day']} {tm['hour']}:{tm['minute']}:{tm['second']}";
                dtti = dtti.astimezone(tz)
                date = datetime.strftime(dtti.date(), '%Y-%m-%d')
                time = f'{dtti.hour}:{dtti.minute}:{dtti.second}'
                date = date+" "+time
                if tm < date:
                    return jsonify(results = {'response_text': 'date and time cannot be less than current date and time'})
                tm = datetime.strptime(tm, '%Y-%m-%d %H:%M:%S')
                job = scheduler.add_job(scheduled, trigger='date', next_run_time = tm, args = [req, flg])
                return jsonify(results = {'response_text': 'OK :)'})

        else:
            return jsonify(results = {'respone_text': 'This type of request is not allowed. :('})
        
    except Exception as e:

        return jsonify(results = {'respone_text': e.args})

if __name__ == '__main__':
    
    app.run(debug=True)
    try:
        while True:
            time.sleep(5)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

