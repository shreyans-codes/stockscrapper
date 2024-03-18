from calendar import c
import datetime
from email.mime.image import MIMEImage
from re import A
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

stockDetailsAllDates = None

# Fetch data for each argument provided
for arg in args:
    stockDetail = getArgStock(arg=arg)
    if(stockDetail is not None):
        stockDetailsAllDates = getStockDetailsAllDates(code=stockDetail.code)
        if(datetime.date.today() == stockDetailsAllDates[0].date):
            #? Today's data is available, no need to run web scrapper
            continue
    # Fetch details and fundamental data using requests
    data_for_args[arg] = {
        'details': requests.get('https://www.topstockresearch.com/rt/Stock/{}/BirdsEyeView'.format(arg), cookies=cookies, headers=headers),
        'fundamentals': requests.get('https://www.topstockresearch.com/rt/Stock/{}/FundamentalAnalysis'.format(arg), cookies=cookies, headers=headers)
    }
    
    # Getting the Birds Eye View Details for the stock
    sexy_body = bs(data_for_args[arg]['details'].content, 'html.parser')
    table_rows = sexy_body.find_all('tr')
    sector = None
    code = None
    close = None
    altman = None
    f_Score = None
    sloan_ratio = 0
    stock = getArgStock(arg=arg)
    
    # Traversing values
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
    
    # If the stock doesn't exist in DB, create a new record
    if stock is None:
            addStock(arg=arg, code=code, sector=sector)
            stock = getArgStock(arg=arg)
    
    # Getting the fundamentals for the stock
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
    
    addStockDetails(close=close, date=datetime.date.today(), altman=altman, f_score=f_Score, sloan=(sloan_ratio *100), s_id=stock.id)


# Dictionary to store sectors and their respective stocks
categorized_stock = []
sector_dict = {}

for index, arg in enumerate(args):
    stock = getArgStock(arg=arg)
    if stock is None:
        continue
    stockDetailsAllDates = getStockDetailsAllDates(code=stock.code)
    sector = stock.sector
    stock_info = None
    five_days_ago = datetime.date.today() - datetime.timedelta(days=5)
    print("Five days ago:", five_days_ago)
    # print(list(stockDetailsAllDates))
    for i, sd in enumerate(stockDetailsAllDates):
        print("Evaluating: ", sd.date)
        if(sd.date <= five_days_ago): # type: ignore
            print("found prev week")
            stock_info = {
                'name': stock.code,
                'close': stockDetailsAllDates[0].close,
                'prev_close': sd.close,
                'altman': stockDetailsAllDates[0].altman_z_score,
                'prev_altman': sd.altman_z_score,
                'f_score': stockDetailsAllDates[0].f_score,
                'prev_f_score': sd.f_score,
                'sloan_ratio': stockDetailsAllDates[0].sloan_ratio,
                'prev_sloan_ratio': sd.sloan_ratio
            }
            break
        
        else:
            print("couldn't find prev week")
            stock_info = {
                'name': stock.code,
                'close': stockDetailsAllDates[0].close,
                'prev_close': sd.close,
                'altman': stockDetailsAllDates[0].altman_z_score,
                'prev_altman': sd.altman_z_score,
                'f_score': stockDetailsAllDates[0].f_score,
                'prev_f_score': sd.f_score,
                'sloan_ratio': stockDetailsAllDates[0].sloan_ratio,
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