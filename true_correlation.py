#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 16:11:46 2022

@author: hack-rafa
"""

import pandas as pd
import os
import numpy as np
import plotly.express as px
from datetime import datetime


allPickleFiles = []
df = pd.DataFrame()

for file in os.listdir():
    if ".pkl" in file:
        allPickleFiles.append(file)

for file in allPickleFiles:
    localDf = pd.read_pickle(file)
    concat = [df, localDf]
    df = pd.concat(concat)

df.drop_duplicates(subset=['Date', 'Event Name', 'Event Rounds', 'Round', 'White Name',
       'Black Name', 'Result', 'White ELO', 'Black ELO', 'Moves',
       'White Av CP Loss', 'Black Av CP Loss', 'Analysis Depth'], inplace=True)

df = df.dropna(subset=['White Name'], axis=0)
df = df.dropna(subset=['Black Name'], axis=0)
df = df.dropna(subset=['White ELO'], axis=0)
df = df.dropna(subset=['Black ELO'], axis=0)
df['White ELO'] = df['White ELO'].apply(lambda x: int(x))
df['Black ELO'] = df['Black ELO'].apply(lambda x: int(x))
df['Moves'] = df['Moves'].apply(lambda x: int(x))
df['White Av CP Loss'] = df['White Av CP Loss'].apply(lambda x: float(x))
df['Black Av CP Loss'] = df['Black Av CP Loss'].apply(lambda x: float(x))
df['Analysis Depth'] = df['Analysis Depth'].apply(lambda x: int(x))
df['Date'] = df['Date'].apply(lambda x: str(x).replace(".", "-").replace("??", "01")[:10])
df['Date'] = df['Date'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))


df.reset_index(inplace=True, drop=True)

whiteRatingDf = pd.DataFrame(columns=['Player', 'Rating', 'CP Loss List', 'Av CP Loss', 'Std. Dev. CP Loss'])
blackRatingDf = pd.DataFrame(columns=['Player', 'Rating', 'CP Loss List', 'Av CP Loss', 'Std. Dev. CP Loss'])

whiteRatingDf['Rating'] = df['White ELO'].copy()
whiteRatingDf['CP Loss List'] = df['White CP Loss List'].copy()
whiteRatingDf['Player'] = df['White Name'].copy()
blackRatingDf['Rating'] = df['Black ELO'].copy()
blackRatingDf['CP Loss List'] = df['Black CP Loss List'].copy()
blackRatingDf['Player'] = df['Black Name'].copy()

correlationDf = pd.concat([whiteRatingDf, blackRatingDf])

# Remove empty players
correlationDf = correlationDf.dropna(subset=['Player'], axis=0)

correlationDf.reset_index(inplace=True, drop=True)
correlationDf['Av CP Loss'] = correlationDf['CP Loss List'].apply(lambda x: np.mean(x))
correlationDf['Std. Dev. CP Loss'] = correlationDf['CP Loss List'].apply(lambda x: np.std(x))
correlationDf.dropna(inplace=True)
correlationDf['Rating'] = correlationDf['Rating'].apply(lambda x: int(x))
correlationDf.reset_index(inplace=True, drop=True)

# show only 10 players since other's games are not complete data set
playerCountDf = correlationDf.groupby(['Player'], sort=False)['Player'].count().reset_index(name='Count')
playerTop10 = playerCountDf.nlargest(10, 'Count')
correlationDfTop10 = pd.merge(left=correlationDf, right=playerTop10, left_on='Player', right_on='Player')

# actual correlation
corrRatingAcpl = correlationDfTop10['Rating'].corr(correlationDfTop10['Av CP Loss'])
print('Actual correlation between rating and Av CP Loss: ', corrRatingAcpl)

# scatter plot
fig = px.scatter(correlationDfTop10, x='Rating', y='Av CP Loss', color='Player', trendline='ols')
fig.show()
