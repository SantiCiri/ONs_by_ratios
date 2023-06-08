# ONs_by_ratios
Mini repo that webscrapps information from argentinean obligaciones negociables and calculates ratios to asess their buy and sell for oportunities.
Notebook is straightforward and should be executed completly every time. Make sure you complete the comprado list with the tickers you already own.
The pdf download is still to be optimized, so it is highly recommended that not many days go by without running it. Else, you'll debug the first cells.

.py is there to automate the webscrap run and .csv update. To run it at 23hs, on linux, just type on cmd:

crontab -e

0 23 * * 1-5 python {path/to/your/.py}

It will plot a plotly plot if today was the opportunity day
