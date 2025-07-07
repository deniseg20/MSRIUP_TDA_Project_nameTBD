# cleaning the CA DMV data - from a tab seperated file to a CSV file
import pandas as pd
import numpy as np

# reading file
df = pd.read_csv('ca_dmv_2024.csv', sep=',')
df = df.dropna(subset=["Counties", "Measure Names"])

# Pivoting data to avoid having to make dictionary ;)
pivot_df = df.pivot_table(index="Counties", 
                        columns="Measure Names", 
                        values="Measure Values", 
                        aggfunc="first").reset_index()
pivot_df.columns.name = None # removing 'Measure Names'
pivot_df.info()  # info about the dataframe 
drop_list = ["MISC VEHICLES *", "IRP VEHICLES **", "FEE EXEMPT VEHICLES"]
pivot_df = pivot_df[~pivot_df['Counties'].isin(drop_list)]

pivot_df.columns = pivot_df.columns.str.lower()  # column names to lower case
pivot_df['counties'] = pivot_df['counties'].str.lower()  # counties to lower case
print(pivot_df['counties'])
int_cols = ['autos', 'motorcycles', 'trailers', 'trucks', 'total vehicles']
pivot_df[int_cols] = pivot_df[int_cols].apply(lambda col: col.astype("Int64")) # float to int 

# changing order of columns so total is last 
pivot_df = pivot_df[['counties'] + int_cols]
pivot_df.info()

#getting out of state, fee exempt and statewide vehicles to the end
## print(pivot_df.loc[pivot_df['counties'] =='out of state',]) # index 33
## print(pivot_df.loc[pivot_df['counties'] =='statewide',]) # index 54

target_rows = [33, 54]

a = pivot_df.drop(index= target_rows)
b = pivot_df.loc[target_rows,]

pivot_df = pd.concat([a, b]).reset_index(drop=True)


# info
#pivot_df.info()
#print(f"Shape: {pivot_df.shape}")
#print(f"Columns: {list(pivot_df.columns)}")

print(pivot_df)

pivot_df.to_csv('ca_dmv_clean24.csv', index=False)
