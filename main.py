import requests
import datetime
from twilio.rest import Client

# The following constants must be defined before usage
# This script is configured to work only for Memorial golf Houston resident accounts
MEMORIAL_GOLF_USERNAME = ""
MEMORIAL_GOLF_PASSWORD = ""
TWILIO_ACC_SID = ""
TWILIO_AUTH_TOKEN = ""
TWILIO_PHONE_NUM_SENDER = ""
TWILIO_PHONE_NUM_RECEIVER = ""

def login():
    url = "https://foreupsoftware.com/index.php/api/booking/users/login"
    payload = {
        'username': MEMORIAL_GOLF_USERNAME,
        'password': MEMORIAL_GOLF_PASSWORD,
        'booking_class_id': '7527',
        'api_key': 'no_limits',
        'course_id': '20945'
    }
    r = requests.post(url, data=payload)
    json = r.json()
    x_auth = json['jwt']

    return x_auth, json

def get_tee_times(date, x_auth):
    cutoff = datetime.datetime.now().date() + datetime.timedelta(days=3)
    booking_class = '7527' if date <= cutoff else '7530'

    url = "https://foreupsoftware.com/index.php/api/booking/times"
    params = {
        'time': 'all',
        'date': date.strftime("%m-%d-%Y"),
        'holes': 'all',
        'players': '0',
        'booking_class': booking_class,
        'schedule_id': '6282',
        'schedule_ids[]': '6282',
        'schedule_ids[]': '7795',
        'specials_only': '0',
        'api_key': 'no_limits'
    }
    headers = {
        'x-authorization': f'Bearer {x_auth}'
    }
    r = requests.get(url, params=params, headers=headers)
    json = r.json()

    return json

def to_string(str_appending, times):
    for dict in times:
        str_appending += f"\t{dict['time']}: Players: {dict['available_spots']}\n"
    return str_appending

def send_sms(message):
    account_sid = TWILIO_ACC_SID
    auth_token = TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_=TWILIO_PHONE_NUM_SENDER,
        body=message,
        to=TWILIO_PHONE_NUM_RECEIVER
    )

    return message.sid

def main():
    today = datetime.datetime.now().date()
    x_auth, login_info = login()
    str_times = "Available Memorial tee times:\n"
    for d in range(4):
        this_day = today + datetime.timedelta(days=d)
        tee_times = get_tee_times(this_day, x_auth)
        str_times += f"Available for {this_day.strftime("%b %d")}:\n"
        str_times = to_string(str_times, tee_times)

    r = send_sms(str_times)
    return r



if __name__=="__main__":
    main()