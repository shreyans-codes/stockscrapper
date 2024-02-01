import datetime
from email.mime.image import MIMEImage
import sys
from turtle import st
import schedule, time
import requests
import config
from bs4 import BeautifulSoup as bs
from jinja2 import Environment, FileSystemLoader
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from database_management import addStock, addStockDetails, getArgStock, getStock, getStockDetails, getStockDetailsAllDates

# Cookies and headers for requests
cookies = config.cookies  # Dictionary containing cookies
headers = config.headers  # Dictionary containing headers

# Fetching command-line arguments
recipient_name = sys.argv[1]
recipient_email = sys.argv[2]
args = sys.argv[3:]
print("Arguments passed:", args)

data_for_args = {}

file_loader = FileSystemLoader('.')
env = Environment(loader=file_loader)
template = env.get_template('template2.html')


# Fetch data for each argument provided
for arg in args:
    # Fetch details and fundamental data using requests
    data_for_args[arg] = {
        'details': requests.get('https://www.topstockresearch.com/rt/Stock/{}/BirdsEyeView'.format(arg), cookies=cookies, headers=headers),
        'fundamentals': requests.get('https://www.topstockresearch.com/rt/Stock/{}/FundamentalAnalysis'.format(arg), cookies=cookies, headers=headers)
    }

# Dictionary to store sectors and their respective stocks
categorized_stock = []
sector_dict = {}

for index, arg in enumerate(args):
    
    sexy_body = bs(data_for_args[arg]['details'].content, 'html.parser')
    table_rows = sexy_body.find_all('tr')
    sector = None
    should_run = True
    res = getArgStock(arg=arg)
    stock_info = None
    if res:
        sector = res.sector
        print("found stock in db")
        stockdetails = getStockDetailsAllDates(res.code)
        print(stockdetails)
        if len(stockdetails)<=0:
            break
        for index, sd in enumerate(stockdetails):
            if datetime.date.today() == sd.date and index+1 < len(stockdetails) and stockdetails[index+1] is not None:
                print("found next")
                stock_info = {
                    'name': res.code,
                    'close': sd.close,
                    'prev_close': stockdetails[index+1].close,
                    'altman': sd.altman_z_score,
                    'prev_altman': stockdetails[index+1].altman_z_score,
                    'f_score': sd.f_score,
                    'prev_f_score': stockdetails[index+1].f_score,
                    'sloan_ratio': sd.sloan_ratio,
                    'prev_sloan_ratio': stockdetails[index+1].sloan_ratio
                }
                should_run = False
            elif datetime.date.today() == sd.date:
                print("only found today")
                stock_info = {
                    'name': res.code,
                    'close': sd.close,
                    'prev_close': sd.close,
                    'altman': sd.altman_z_score,
                    'prev_altman': sd.altman_z_score,
                    'f_score': sd.f_score,
                    'prev_f_score': sd.f_score,
                    'sloan_ratio': sd.sloan_ratio,
                    'prev_sloan_ratio': sd.sloan_ratio
                }
                should_run = False
            
            
    if should_run:
    # Loop through rows to find data in table cells (td)
        for row in table_rows:
            cells = row.find_all('td')
            if len(cells) == 2:
                label = cells[0].text.strip()
                value = cells[1].text.strip()
                # Extract necessary data based on labels
                if label.startswith("Sect"):
                    sector = value
                if label.startswith("Close"):
                    close = float(value)
                if label.startswith("Code"):
                    code = value
                # print(f"{label}: {value}")

        # print("\n------Details-------\n")

        sexy_body = bs(data_for_args[arg]['fundamentals'].content, 'html.parser')
        table_rows = sexy_body.find_all('tr')

        # Loop through rows to find data in table cells (td)
        for row in table_rows:
            cells = row.find_all('td')
            if len(cells) == 2:
                label = cells[0].text.strip()
                value = cells[1].text.strip()
                # Extract specific data based on labels
                if label.startswith("Altman"):
                    altman = round(float(value),2)
                if label.startswith("Piotroski"):
                    f_Score = int(float(value))
                if label.startswith("Sloan"):
                    sloan_ratio = round(float(value), 2)
                # print(f"{label}: {value}")

        # print("\n--------------------\n")
        if getArgStock(arg=arg) is None:
            addStock(arg=arg, code=code, sector=sector)
        sd = getStockDetails(code)
        if not sd:
            stock = getStock(code)
            addStockDetails(close=close, date=datetime.date.today(), altman=altman, f_score=f_Score, sloan=(sloan_ratio *100), s_id=stock.id)
            sd = getStockDetails(code)
            print("New sd = ", sd.altman_z_score, "\n")
        else:
            stock = getStock(code)
            addStockDetails(close=close, date=datetime.date.today(), altman=altman, f_score=f_Score, sloan=(sloan_ratio *100), s_id=stock.id)
        
        print("sd = ", sd.altman_z_score, "\n")
        

        stock_info = {
            'name': code,
            'close': close,
            'prev_close': sd.close,
            'altman': altman,
            'prev_altman': sd.altman_z_score,
            'f_score': f_Score,
            'prev_f_score': sd.f_score,
            'sloan_ratio': (sloan_ratio *100),
            'prev_sloan_ratio': sd.sloan_ratio
        }
    
    # Store stocks under respective sectors in the 'sectors' dictionary
    if sector_dict.get(sector):
        sector_dict[sector].append(stock_info)
    else:
        sector_dict[sector] = [stock_info]


for sector, stocks in sector_dict.items():
    categorized_stock.append({'name': sector, 'stocks': stocks})

html_content = template.render(sectors=categorized_stock, recipient_name = recipient_name)

# Function to send daily email
def send_daily_email():
    # Construct email message
    msg = MIMEMultipart()
    msg['Subject'] = recipient_name + ' Portfolio Status'
    # recipients = ['shreyans.sethia@skiff.com', 'amnrj1622@gmail.com']
    # msg['To'] =  ", ".join(recipients)
    msg['From'] = config.email_username
    msg['To'] =  recipient_email
    html = html_content
    # Attach HTML content to the email
    msg.attach(MIMEText(html, 'html'))


    # SMTP server settings for Gmail
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # Port for TLS
    username = config.email_username
    password = config.email_password

    try:
        # Connect to SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(username, password)
            smtp.send_message(msg)
        print("Email with image sent successfully!")
    except Exception as e:
        print("Error sending email:", e)

#? Uncomment these lines to schedule send, currently congigured for task schedular

# Schedule daily emails at specific times
# def job():
#     print("Sending email...")

# schedule.every(10).seconds.do(send_daily_email)
# schedule.every().day.at('08:00').do(send_daily_email)
# schedule.every().day.at('16:00').do(send_daily_email)

# Continuously check and run scheduled tasks
# while True:
#     schedule.run_pending()

send_daily_email()