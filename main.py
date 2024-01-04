import sys
import schedule, time
import requests
import config
from bs4 import BeautifulSoup as bs
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


args = sys.argv[1:]

print("Arguments passed:", args)

cookies = {
    'JSESSIONID': 'C6066D538BC5D47B824C0A073B3CCDA5.rtnode2',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.topstockresearch.com/rt/Stock/GMRP&UI/BirdsEyeView',
    'Connection': 'keep-alive',
    # 'Cookie': 'JSESSIONID=C6066D538BC5D47B824C0A073B3CCDA5.rtnode2',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Sec-GPC': '1',
}

def send_daily_email():
    msg = MIMEMultipart()
    msg['Subject'] = 'Email with Image'
    msg['From'] = config.email_username
    msg['To'] = 'shreyans.sethia@skiff.com'
    html = """\
    <html>
      <body>
        <p>Hello!<br>
        </p>
      </body>
    </html>
    """
    # Attach HTML content to the email
    msg.attach(MIMEText(html, 'html'))

    # Gmail SMTP server settings
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # Port for TLS

    username = config.email_username
    password = config.email_password

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(username, password)
            smtp.send_message(msg)
        print("Email with image sent successfully!")
    except Exception as e:
        print("Error sending email:", e)


def job():
    print("Sending email...")

schedule.every().day.at('08:00').do(send_daily_email)
schedule.every().day.at('16:00').do(send_daily_email)


response = requests.get(
    'https://www.topstockresearch.com/rt/Stock/GMRP&UI/FundamentalAnalysis',
    cookies=cookies,
    headers=headers,
)

sexy_body = bs(response.content, 'html.parser')

table_rows = sexy_body.find_all('tr')

# Loop through rows to find the data in table cells (td)
for row in table_rows:
    cells = row.find_all('td')
    if len(cells) == 2:  # Assuming each row has two cells (label and value)
        label = cells[0].text.strip()
        value = cells[1].text.strip()
        print(f"{label}: {value}")

while True:
    schedule.run_pending()
    time.sleep(60)
