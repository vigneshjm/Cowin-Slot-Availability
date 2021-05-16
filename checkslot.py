import requests
import json
from datetime import datetime
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from jproperties import Properties
import base64

configs = Properties()
with open('inputparam.properties', 'rb') as config_file:
    configs.load(config_file)

chk_date = str(configs.get("date").data)
chk_district = str(configs.get("districtCode").data)
chk_mail = str(configs.get("mail_recipient").data)


browser_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}

# st_response = requests.get(ST_URL, headers=browser_header)
# state_list = json.loads(st_response.text)
# for i in state_list['states']:
#   dt_response = requests.get(DT_URL+str(i['state_id']), headers=browser_header)
#   district_list = json.loads(dt_response.text)
#   for j in district_list['districts']:
#     print(str(j['district_id'])+" - "+ j['district_name'])

if(chk_date == '' or chk_district == '' or chk_mail == ''):
  print("Input Parameter missing")
  exit(1)

format = "%d-%m-%Y"
try:
  datetime.datetime.strptime(chk_date, format)
except:
  raise ValueError("Incorrect date format, should be DD-MM-YYYY")

ST_URL = "https://cdn-api.co-vin.in/api/v2/admin/location/states"
DT_URL = "https://cdn-api.co-vin.in/api/v2/admin/location/districts/" # append state id fetched from ST_URL # 
URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={dist}&date={cdate}".format(dist = chk_district, cdate = chk_date)


availability = []
response = requests.get(URL, headers=browser_header)
if (response.ok) and ('centers' in json.loads(response.text)):
    resp_json = json.loads(response.text)['centers']
    for i in resp_json:       
        for j in i['sessions']:
            center = {}
            if(j['available_capacity'] > 0 and j['min_age_limit'] == 18 and j['date'] == chk_date):
                center['slots'] = j['slots']
                center['date'] = j['date']
                center['capacity'] = j['available_capacity']
                center['cid'] = i['center_id']
                center['name'] = i['name']
                center['address'] = i['address']
            if bool(center):
                availability.append(center)

print(availability)
final_df = ''
if availability:
  for i in availability:
    final_df = final_df + '<tr><td>'+str(','.join(i['slots']))+'</td><td>'+str(i['date'])+'</td><td>'+str(i['capacity'])+'</td><td>'+str(i['cid'])+'</td><td>'+str(i['name'])+'</td><td>'+str(i['address'])+'</td></tr>'

emaillist = chk_mail
msg = MIMEMultipart()
msg['Subject'] = "Covid Vaccination Slot"
msg['From'] = 'vignesjm96@gmail.com'

html_unavailable = """\
<html>
<head>
</head>
<body>
<h1>Vaccination slots not available for given date
</html>"""

html_available = """\
<html>
  <head>
  </head>
  <body>
  <table style="width:100%" style="border: 1px solid black;">
  <tr>
    <th>slots</th>
    <th>date</th> 
    <th>capacity</th>
    <th>id</th>
    <th>name</th> 
    <th>address</th>
  </tr>
    {0}
  </table>
  </body>
</html>
""".format(final_df)

if availability:
  mail_html = html_available
else:
  mail_html = html_unavailable

part1 = MIMEText(mail_html, 'html')
msg.attach(part1)

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
mailid = str(base64.b64decode("dmlnbmVzaGptOTZAZ21haWwuY29t").decode("utf-8"))
pwd = str(base64.b64decode("ZWhsbyBnbGxoIGVybnogYXd3ZQ==").decode("utf-8"))
server.login(mailid , pwd)
server.sendmail(msg['From'], emaillist , msg.as_string())