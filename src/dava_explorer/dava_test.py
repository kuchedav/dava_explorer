import pandas as pd

from dava_explorer.dava import analyze_table

df = pd.read_csv("./src/dava_explorer/country_indicators.csv")

analyze_table(df)
