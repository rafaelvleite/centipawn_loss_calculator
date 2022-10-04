#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 16:11:46 2022

@author: hack-rafa
"""

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from datetime import datetime

filterByPlayer = True

playerName = "Esipenko"
playerName = "Firouzja"
playerName = "Rausis"
playerName = "Erigaisi"
playerName = "Gukesh"
playerName = "Keymer"
playerName = "Pragg"
playerName = "Carlsen"
playerName = "Caruana"
playerName = "Niemann"


filterByMinDate = False
minDate = "2018-01-01"

filterByMaxDate = False
maxDate = "2018-01-01"

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


# Filter by Player
if filterByPlayer == True:
    df1 = df[df['White Name'].str.contains(playerName)].copy()
    df2 = df[df['Black Name'].str.contains(playerName)].copy()
    df = pd.concat([df1, df2])
    df.reset_index(inplace=True, drop=True)
    
# Filter by min date
if filterByMinDate == True:
    df = df.query('Date >= "' + minDate + '"').copy()

if filterByMaxDate == True:
    df = df.query('Date < "' + minDate + '"').copy()


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
# Remove cheater Igor Rausis
if "rausis" not in playerName.lower():
    correlationDf = correlationDf[~correlationDf['Player'].str.contains("Rausis")].copy()
# Remove Niemann to be on the safe side
if "niemann" not in playerName.lower():
    correlationDf = correlationDf[~correlationDf['Player'].str.contains("Niemann")].copy()
# Filter by Player
if filterByPlayer == True:
    correlationDf = correlationDf[correlationDf['Player'].str.contains(playerName)].copy()

correlationDf.reset_index(inplace=True, drop=True)
correlationDf['Av CP Loss'] = correlationDf['CP Loss List'].apply(lambda x: np.mean(x))
correlationDf['Std. Dev. CP Loss'] = correlationDf['CP Loss List'].apply(lambda x: np.std(x))
correlationDf.dropna(inplace=True)
correlationDf['Rating'] = correlationDf['Rating'].apply(lambda x: int(x))
correlationDf.reset_index(inplace=True, drop=True)

# Classify rating in tiers
d = {
     range(1400, 1500): 1400,
     range(1500, 1600): 1500,
     range(1600, 1700): 1600,
     range(1700, 1800): 1700,
     range(1800, 1900): 1800,
     range(1900, 2000): 1900,
     range(2000, 2100): 2000,
     range(2100, 2200): 2100,
     range(2200, 2300): 2200, 
     range(2300, 2400): 2300, 
     range(2400, 2500): 2400, 
     range(2500, 2600): 2500, 
     range(2600, 2700): 2600,
     range(2700, 2800): 2700,
     range(2800, 2900): 2800
     }
correlationDf['Tier'] = correlationDf['Rating'].apply(lambda x: next((v for k, v in d.items() if x in k), 0))
correlationDf['Games'] = 1

groupedCorrelationDf = correlationDf.groupby('Tier').agg({'Rating': np.mean, 'Av CP Loss': np.mean, 'Std. Dev. CP Loss': np.mean, 'Games': np.sum})
#groupedCorrelationDf = groupedCorrelationDf[groupedCorrelationDf['Rating'] >=2200] # Uncomment this line in case you want to look only after 2200 and get more consistent data
groupedCorrelationDf = groupedCorrelationDf[groupedCorrelationDf['Games'] >=30] # Stattistical relevance
groupedCorrelationDf = groupedCorrelationDf[groupedCorrelationDf.index > 0]
print(groupedCorrelationDf[['Rating', 'Av CP Loss', 'Std. Dev. CP Loss']].corr(method='pearson'))
dfToPlot = groupedCorrelationDf[['Rating', 'Av CP Loss', 'Std. Dev. CP Loss']].copy()

f = plt.figure(figsize=(19, 15))
plt.matshow(dfToPlot.corr(method='pearson'), fignum=f.number)
plt.xticks(range(dfToPlot.select_dtypes(['number']).shape[1]), dfToPlot.select_dtypes(['number']).columns, fontsize=14, rotation=45)
plt.yticks(range(dfToPlot.select_dtypes(['number']).shape[1]), dfToPlot.select_dtypes(['number']).columns, fontsize=14)
cb = plt.colorbar()
cb.ax.tick_params(labelsize=14)
plt.title('Correlation Matrix', fontsize=16);
plt.show()
plt.clf()

plt.matshow(dfToPlot.corr(method='pearson'))
plt.show()


# Rating x ACTPL Linear Regression
dfToPlot
X = dfToPlot.index.values.reshape(-1, 1)
y = dfToPlot.iloc[:, 1:2].values


# Fitting Linear Regression to the dataset
from sklearn.linear_model import LinearRegression
lin = LinearRegression()  
lin.fit(X, y)

# Visualising the Linear Regression results
plt.scatter(X, y, color = 'blue')
plt.plot(X, lin.predict(X), color = 'red')
plt.title('ACPL by Rating')
plt.xlabel('Rating')
plt.ylabel('Av CP Loss')
plt.show()
plt.clf()


# Rating x STDCPL Loss Linear Regression
dfToPlot
X = dfToPlot.index.values.reshape(-1, 1)
y = dfToPlot.iloc[:, 2:3].values

# Fitting Linear Regression to the dataset
from sklearn.linear_model import LinearRegression
lin2 = LinearRegression()  
lin2.fit(X, y)

# Visualising the Linear Regression results
plt.scatter(X, y, color = 'blue')
plt.plot(X, lin2.predict(X), color = 'red')
plt.title('STDCPL by Rating')
plt.xlabel('Rating')
plt.ylabel('S. Dev CP Loss')
plt.show()
plt.clf()


summary = correlationDf['Player'].copy()
# concatenar as palavras
all_summary = " ".join(s for s in summary)
# lista de stopword
stopwords = set(STOPWORDS)
stopwords.update(["da", "meu", "em", "você", "de", "ao", "os"])
# gerar uma wordcloud
wordcloud = WordCloud(stopwords=stopwords,
                      background_color="black",
                      width=1600, height=800).generate(all_summary)
# mostrar a imagem final
fig, ax = plt.subplots(figsize=(10,6))
ax.imshow(wordcloud, interpolation='bilinear')
ax.set_axis_off()
plt.imshow(wordcloud);
wordcloud.to_file("playersWordcloud.png")
print(groupedCorrelationDf)


