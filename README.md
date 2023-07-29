# ONs_by_ratios
Mini repo that webscrapps information from argentinean obligaciones negociables and calculates ratios to asess their buy and sell for oportunities.
Executing .py to run the program under the hood. See notebook to check the details step by step.

The pdf download is still to be optimized, so it is highly recommended that not many days go by without running it. Else, you'll debug the first cells.

To run it at 23hs, on linux, just type on cmd:

crontab -e

0 23 * * 1-5 python {path/to/your/.py}

It will plot a plotly plot if today was the opportunity day
