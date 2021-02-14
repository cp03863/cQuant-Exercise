#!/usr/bin/env python
# coding: utf-8

# # Setup

# In[5]:


import numpy as np
import pandas as pd
import os


# In[74]:


jp = os.path.join
parent_dir = "C:\\Users\\chris\\Desktop\\cQuant Exercise\\"
data_dir = jp(parent_dir, "Data")
output_dir = jp(parent_dir, "Outputs")


# # Task 1

# In[15]:


fnames = os.listdir(data_dir)
data = pd.concat([pd.read_csv(jp(data_dir,f)) for f in fnames ])


# # Task 2

# In[83]:


print("Attributes: ", data.columns.values, "\nShape: ", data.shape)


# In[192]:


data['Date'] = pd.to_datetime(data['Date'],infer_datetime_format = True)


# In[35]:


#Set periods at each month-year
per = data.Date.dt.to_period("M")


# In[45]:


MoY_Avg = data.groupby([per,'SettlementPoint']).mean()


# In[41]:


#data.groupby([per,'SettlementPoint']).mean()


# # Task 3

# In[58]:


#Formatting Dates
MoY_Avg.reset_index(inplace=True)
MoY_Avg['Month']=MoY_Avg['Date'].apply(lambda x: str(x)[-2:])
MoY_Avg['Year'] = MoY_Avg['Date'].apply(lambda x: str(x)[:4])


# In[64]:


#Formatting Table
MoY_Avg.drop("Date",1, inplace = True)
MoY_Avg = MoY_Avg[['SettlementPoint',"Year",'Month','Price']]
MoY_Avg.rename(columns = {'Price': "AveragePrice"}, inplace= True)


# In[76]:


#Output
MoY_Avg.to_csv(jp(output_dir, "AveragePriceByMonth.csv"),index=False)


# # Task 4

# In[95]:


hubs = [ele for ele in data['SettlementPoint'].unique() if ele.startswith("HB_")]
print("Settlement Hubs: ",hubs)


# In[136]:


data["Year"] = data['Date'].dt.year


# In[114]:


target = data[data['SettlementPoint'].isin(hubs)]
target["Year"] = target['Date'].dt.year


# In[181]:


def hourly_price_volatility(df):
    output = []
    for hub in hubs:
        subset = df[df['SettlementPoint']==hub]
        for y in df['Year'].unique():
            subset2 = subset[subset['Year']==y]
            subset2['returns']=(subset2['Price']/subset2['Price'].shift(-1))

            pos_vals = subset2[subset2["returns"]>0]
            pos_vals['returns'] = np.log(pos_vals['returns'])
            pos_vals.replace([np.inf, -np.inf], np.nan,inplace=True)
            pos_vals.dropna(inplace=True)
            
            sd = np.std(pos_vals['returns'])
            hvol = sd*np.sqrt(len(pos_vals['returns']))
            
            output.append((hub,y,hvol))
            
    output = pd.DataFrame(output, columns = ["SettlementPoint","Year","HourlyVolatility"])
    
    
    return output
        


# In[182]:


t5 = hourly_price_volatility(target)


# In[183]:


t5


# # Task 5

# In[184]:


#Output
t5.to_csv(jp(output_dir,"HourlyVolatilityByYear.csv"),index=False)


# # Task 6

# In[190]:


#Shows the settlement hub with the highest overall volatility in each year
MaxVol = t5.groupby("Year").max()
MaxVol.to_csv(jp(output_dir,"MaxVolatilityByYear.csv"),index=True)


# # Task 7

# In[210]:


def formatting(df):
    for point in df['SettlementPoint'].unique():
        subset = df[df['SettlementPoint']==point]
        subset['hour'] = subset['Date'].dt.hour
        
        xform = subset.pivot_table(index=subset['Date'].dt.date, columns='hour', values='Price')
        xform.reset_index(inplace=True)
        xform.insert(0,'Variable', point)
        fname = "spot_" +point+".csv"
        xform.to_csv(jp(output_dir,"formattedSpotHistory\\",fname),index=False)
        print(point, " data formatted and saved.")
    return 'Formatting Complete'


# In[211]:


formatting(data)


# # Mean Plots
# 

# In[ ]:


import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')


# In[212]:


hubs = [ele for ele in data['SettlementPoint'].unique() if ele.startswith("HB_")]
zones = [ele for ele in data['SettlementPoint'].unique() if ele.startswith("LZ_")]


# To complete plots: take a subset of the monthly average prices dataframe for both hubs and zones
# use matplotlib's plotting functions to build a multiple line plot, using a different color to plot each hub or zone
# Set time (month-year) across the x-axis, Average price up the y-axis
