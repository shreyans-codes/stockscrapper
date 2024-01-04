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

# Lists to store details and fundamental data for each argument
details = []
fundamentals = []

# Fetch data for each argument provided
for arg in args:
    # Fetch details and fundamental data using requests
    details.append(requests.get('https://www.topstockresearch.com/rt/Stock/{}/BirdsEyeView'.format(arg), cookies=cookies, headers=headers))
    fundamentals.append(requests.get('https://www.topstockresearch.com/rt/Stock/{}/FundamentalAnalysis'.format(arg), cookies=cookies, headers=headers))

# Dictionary to store sectors and their respective stocks
sectors = {}

# Extract details from the 'details' responses
for response in details:
    sexy_body = bs(response.content, 'html.parser')
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
            print(f"{label}: {value}")

    print("\n------Details-------\n")

    # Store stocks under respective sectors in the 'sectors' dictionary
    if sector in sectors:
        sectors[sector]['stocks'].append({'name': code, 'close': close})
    else:
        sectors[sector] = {'name': sector, 'stocks': [{'name': code, 'close': close}]}
print(sectors)

# Extract specific data from the 'fundamentals' responses
for response in fundamentals:
    sexy_body = bs(response.content, 'html.parser')
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
            print(f"{label}: {value}")
    
    print("\n--------------------\n")

# Function to send daily email
def send_daily_email():
    # Construct email message
    msg = MIMEMultipart()
    msg['Subject'] = 'Email with Image'
    msg['From'] = config.email_username
    msg['To'] = 'shreyans.sethia@skiff.com'
    html = """\
    <html>
      <body>
        <p>Hello!<br></p>
      </body>
    </html>
    """
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

schedule.every().day.at('08:00').do(send_daily_email)
schedule.every().day.at('16:00').do(send_daily_email)

# Continuously check and run scheduled tasks
while True:
    schedule.run_pending()
    time.sleep(60)
