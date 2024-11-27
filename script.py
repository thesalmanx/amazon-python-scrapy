import pandas as pd
import ssl
# Create an SSL context that ignores certificate errors
ssl._create_default_https_context = ssl._create_unverified_context

article = pd.read_html('https://dailyfinancego.com/tax-free-savings-account-tfsa-definition-and-calculation/')
print(len(article))
print(article)