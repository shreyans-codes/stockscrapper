# Note
You can find the latest version of the project [-> here <-](https://github.com/riyavij2001/TrackMyStock)

# stockscrapper
A simple and effective CLI tool to send emails about stocks in your portfolio.

## Description
A CLI tool that you cna set up as a CRON job that will automatically keep sending you emails about your stocks and their current health.

The stocks are divided into sectors. Each stock has the following fields:
- **Altman Z Score:** Investors can use Altman Z-score Plus to evaluate corporate credit risk. A score below 1.8 signals the company is likely headed for bankruptcy, while companies with scores above 3 are not likely to go bankrupt. 
- **Piotroski F Score:** The Piotroski F-Score is a scoring system designed to assess the financial strength of a company. If a company has a score of 8 or 9, it is considered a good value. If the score adds up to between 0-2 points, the stock is considered weak. 
- **Sloan Ratio:** If the **Sloan Ratio is between -10% and 10%**, the company is in the _safe zone_ and there is no funny business with accruals.
    - If the Sloan Ratio is less than **between -25% and -10% on the negative side**, and **between 10% and 25% on the positive side**, this is a _warning stage_ of accrual build up.
    
    - If the **Sloan Ratio is less than -25% or greater than 25%**, and this ratio is consistent over several quarters or even years, be careful. Earnings are highly likely to be made up of accruals.


## Motivation
I wanted a quick view of all my stock **seperated by Sectors** and there was no good tool available that did that in a neat way.

Further, I also needed it to **indicate any dangers** to my portfolio.

I had already done my due diligence before buying the stock, now I needed something alert me about any dangers to my portfolio

## Quick Start
Follow the steps to run the program locally:

#### Clone Repository
```bash
git clone https://github.com/shreyans-codes/stockscrapper.git

cd stockscrapper
```

#### Install requirements
```bash
pip install -r requirements.txt
```


#### Run the program
```shell
python.exe main.py <your@email.com> <STOCK SYMBOLS LIKE:> HDFCBANK INFY
```
