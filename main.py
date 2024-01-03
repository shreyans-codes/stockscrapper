import requests
from bs4 import BeautifulSoup as bs

url = 'https://www.topstockresearch.com/rt/Stock/GMRP&UI/FundamentalAnalysis'
response = requests.get(url)

soup = bs(response.content, 'html.parser')

print(response)


table_rows = soup.find_all('tr')

# Loop through rows to find the data in table cells (td)
for row in table_rows:
    cells = row.find_all('td')
    if len(cells) == 2:  # Assuming each row has two cells (label and value)
        label = cells[0].text.strip()
        value = cells[1].text.strip()
        print(f"{label}: {value}")
