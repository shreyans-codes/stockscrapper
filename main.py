import sys
import schedule, time
import requests
import config
from bs4 import BeautifulSoup as bs
from jinja2 import Environment, FileSystemLoader
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

# Cookies and headers for requests
cookies = config.cookies  # Dictionary containing cookies
headers = config.headers  # Dictionary containing headers

# Fetching command-line arguments
args = sys.argv[1:]
print("Arguments passed:", args)

data_for_args = {}

file_loader = FileSystemLoader('.')
env = Environment(loader=file_loader)
template = env.get_template('template.html')


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
                altman = float(value)
            if label.startswith("Piotroski"):
                f_Score = int(float(value))
            if label.startswith("Sloan"):
                sloan_ratio = float(value)
            # print(f"{label}: {value}")

    # print("\n--------------------\n")

    stock_info = {
        'name': code,
        'close': close,
        'altman': altman,
        'f_score': f_Score,
        'sloan_ratio': (sloan_ratio *100)
    }

    # Store stocks under respective sectors in the 'sectors' dictionary
    if sector_dict.get(sector):
        sector_dict[sector].append(stock_info)
    else:
        sector_dict[sector] = [stock_info]


for sector, stocks in sector_dict.items():
    categorized_stock.append({'name': sector, 'stocks': stocks})

for val in categorized_stock:
    print(val['stocks'])
    for stock in val['stocks']:
        print("Stock name: ", stock['name'])



html_content = template.render(sectors=categorized_stock)
    
#! Issue: How to map response and fundamentals to the same arg

# Function to send daily email
def send_daily_email():
    # Construct email message
    msg = MIMEMultipart()
    msg['Subject'] = 'StockScrapper Portfolio Status'
    recipients = ['shreyans.sethia@skiff.com', 'riyavij2001@gmail.com']
    msg['From'] = config.email_username
    msg['To'] =  ", ".join(recipients)
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

# Schedule daily emails at specific times
def job():
    print("Sending email...")

schedule.every(10).seconds.do(send_daily_email)
schedule.every().day.at('08:00').do(send_daily_email)
schedule.every().day.at('16:00').do(send_daily_email)

# Continuously check and run scheduled tasks
while True:
    schedule.run_pending()
