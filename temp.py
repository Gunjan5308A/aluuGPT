import polars as pl

df = pl.read_csv("temp.csv")
print(df.to_string())