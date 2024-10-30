# tools for from csv to excel 

import pandas as pd

# Assuming df is your DataFrame loaded from the CSV
df = pd.read_csv("netflixuserbase.csv")
# Save DataFrame to Excel
df.to_excel("netflixoutput.xlsx", index=False, header=True)
