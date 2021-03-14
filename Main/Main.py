#!/usr/bin/env python
# coding: utf-8

# In[1]:


#######################################################################################
# BSD 2-Clause License

# Copyright (c) 2021, Ferrariic
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, 
    # this list of conditions and the following disclaimer.

 #2. Redistributions in binary form must reproduce the above copyright notice, 
    # this list of conditions and the following disclaimer in the documentation 
    # and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#######################################################################################

import pickle
import time
import datetime
from datetime import date
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D 
import sklearn.cluster
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn.datasets import make_blobs
from sklearn import datasets
from sklearn import metrics
from sklearn.preprocessing import scale
from sklearn.preprocessing import Normalizer
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import MiniBatchKMeans
from sklearn import metrics
from scipy.spatial.distance import cdist
import scipy.stats as stats
from IPython.display import clear_output
import seaborn as sns
import collections
from yellowbrick.cluster import SilhouetteVisualizer
from yellowbrick.cluster import InterclusterDistance
from yellowbrick.datasets import load_nfl
import tensorflow as tf


#PLAYERDATA_FILE1 = np.array(pickle.load(open("PLAYER_DATA_PICKLE4.pickle", "rb")), dtype=object) #file 1 name (new file)
PLAYERDATA_FILE2 = np.array(pickle.load(open("PLAYERSHISCORES.pickle", "rb")), dtype=object) #file 2 name (old file)

#ENTRIES_FILE1 = 0
ENTRIES_FILE2 = 0

#print("FILE1: ",ENTRIES_FILE1, "SHAPE:",np.shape(PLAYERDATA_FILE1))
print("FILE2: ",ENTRIES_FILE2,"SHAPE:",np.shape(PLAYERDATA_FILE2))

#PLAYERDATA = np.concatenate((PLAYERDATA_FILE1, PLAYERDATA_FILE2)) 

PLAYERDATA = PLAYERDATA_FILE2
ENTRIES = PLAYERDATA.shape[0]

with open("PLAYER_DATA_PICKLE5.pickle", "wb") as PLAYER_DATA_PICKLE: #STORES DATA AS .PICKLE (Use N+1 to avoid overwrite)
    pickle.dump(PLAYERDATA, PLAYER_DATA_PICKLE)

print("NUMBER OF ENTRIES: ",ENTRIES)
########################################################
ID = 0 

#SKILLS
PLAYER_NAME = []
PLAYER_TOTAL = [] 
PLAYER_ATTACK = []
PLAYER_DEFENCE = []
PLAYER_STRENGTH = []
PLAYER_HITPOINTS = []
PLAYER_RANGED = []
PLAYER_PRAYER = []
PLAYER_MAGIC = []
PLAYER_COOKING = []
PLAYER_WOODCUTTING = []
PLAYER_FLETCHING = []
PLAYER_FISHING = []
PLAYER_FIREMAKING = []
PLAYER_CRAFTING = []
PLAYER_SMITHING = []
PLAYER_MINING = []
PLAYER_HERBLORE = []
PLAYER_AGILITY = []
PLAYER_THIEVING = []
PLAYER_SLAYER = []
PLAYER_FARMING = []
PLAYER_RUNECRAFT = []
PLAYER_HUNTER = []
PLAYER_CONSTRUCTION = []

#BOSS/CLUES
PLAYER_LEAGUE = [] ##check
PLAYER_BOUNTY_HUNTER_HUNTER = []
PLAYER_BOUNTY_HUNTER_ROGUE = []
PLAYER_CS_ALL = []
PLAYER_CS_BEGINNER = []
PLAYER_CS_EASY  = []
PLAYER_CS_MEDIUM  = []
PLAYER_CS_HARD  = []
PLAYER_CS_ELITE = []
PLAYER_CS_MASTER = []
PLAYER_LMS_RANK = []
PLAYER_SOUL_WARS_ZEAL = []
PLAYER_ABYSSAL_SIRE = []
PLAYER_ALCHEMICAL_HYDRA = []
PLAYER_BARROWS_CHESTS = []
PLAYER_BRYOPHYTA = []
PLAYER_CALLISTO = []
PLAYER_CERBERUS = []
PLAYER_CHAMBERS_OF_XERIC = []
PLAYER_CHAMBERS_OF_XERIC_CHALLENGE_MODE = []
PLAYER_CHAOS_ELEMENTAL = []
PLAYER_CHAOS_FANATIC = []
PLAYER_COMMANDER_ZILYANA = []
PLAYER_CORPOREAL_BEAST = []
PLAYER_CRAZY_ARCHAEOLOGIST = []
PLAYER_DAGANNOTH_PRIME = []
PLAYER_DAGANNOTH_REX = []
PLAYER_DAGANNOTH_SUPREME = []
PLAYER_DERANGED_ARCHAEOLOGIST = []
PLAYER_GENERAL_GRAARDOR = []
PLAYER_GIANT_MOLE = []
PLAYER_GROTESQUE_GUARDIANS = []
PLAYER_HESPORI = []
PLAYER_KALPHITE_QUEEN = []
PLAYER_KING_BLACK_DRAGON = []
PLAYER_KRAKEN = []
PLAYER_KREEARRA = []
PLAYER_KRIL_TSUTSAROTH = []
PLAYER_MIMIC = []
PLAYER_NIGHTMARE = []
PLAYER_OBOR = []
PLAYER_SARACHNIS = []
PLAYER_SCORPIA = []
PLAYER_SKOTIZO = []
PLAYER_THE_GAUNTLET = []
PLAYER_THE_CORRUPTED_GAUNTLET = []
PLAYER_THEATRE_OF_BLOOD = []
PLAYER_THERMONUCLEAR_SMOKE_DEVIL = []
PLAYER_TZKAL_ZUK = []
PLAYER_TZTOK_JAD = []
PLAYER_VENENATIS = []
PLAYER_VETION = []
PLAYER_VORKATH = []
PLAYER_WINTERTODT = []
PLAYER_ZALCANO = []
PLAYER_ZULRAH = []

PLAYER_ALL = [] #summation of group
PLAYER_IND = [] #individualized data (k-means orientation)

for name,scores in PLAYERDATA:
    PLAYER_NAME.append(name) #pulls name
    #ID += 1
    #PLAYER_IND.append(ID)
    
    #for skills in scores[:1]:
        #PLAYER_TOTAL.append(skills[2]) #pulls total level
        #PLAYER_IND.append(skills[2])
        
    for skills in scores[1:2]: 
        PLAYER_ATTACK.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[2:3]:
        PLAYER_DEFENCE.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[3:4]:
        PLAYER_STRENGTH.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[4:5]:
        PLAYER_HITPOINTS.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[5:6]:
        PLAYER_RANGED.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[6:7]:
        PLAYER_PRAYER.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[7:8]:
        PLAYER_MAGIC.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[8:9]:
        PLAYER_COOKING.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[9:10]:
        PLAYER_WOODCUTTING.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[10:11]:
        PLAYER_FLETCHING.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[11:12]:
        PLAYER_FISHING.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[12:13]:
        PLAYER_FIREMAKING.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[13:14]:
        PLAYER_CRAFTING.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[14:15]:
        PLAYER_SMITHING.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[15:16]:
        PLAYER_MINING.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[16:17]:
        PLAYER_HERBLORE.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[17:18]:
        PLAYER_AGILITY.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[18:19]:
        PLAYER_THIEVING.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[19:20]:
        PLAYER_SLAYER.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[20:21]:
        PLAYER_FARMING.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[21:22]:
        PLAYER_RUNECRAFT.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[22:23]:
        PLAYER_HUNTER.append(skills[2])
        PLAYER_IND.append(skills[2])
        
    for skills in scores[23:24]:
        PLAYER_CONSTRUCTION.append(skills[2])
        PLAYER_IND.append(skills[2])
        
################## BOSSES AND CLUES ###################
    for skills in scores[24:25]:
        PLAYER_LEAGUE.append(skills[1])
        PLAYER_IND.append(skills[1])
    
    for skills in scores[25:26]:
        PLAYER_BOUNTY_HUNTER_HUNTER.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[26:27]:
        PLAYER_BOUNTY_HUNTER_ROGUE.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[27:28]:
        PLAYER_CS_ALL.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[28:29]:
        PLAYER_CS_BEGINNER.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[29:30]:
        PLAYER_CS_MEDIUM.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[30:31]:
        PLAYER_CS_HARD.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[31:32]:
        PLAYER_CS_ELITE.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[32:33]:
        PLAYER_CS_MASTER.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[33:34]:
        PLAYER_LMS_RANK.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[34:35]:
        PLAYER_SOUL_WARS_ZEAL.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[35:36]:
        PLAYER_ABYSSAL_SIRE.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[36:37]:
        PLAYER_ALCHEMICAL_HYDRA.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[37:38]:
        PLAYER_BARROWS_CHESTS.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[38:39]:
        PLAYER_BRYOPHYTA.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[39:40]:
        PLAYER_CALLISTO.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[40:41]:
        PLAYER_CERBERUS.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[41:42]:
        PLAYER_CHAMBERS_OF_XERIC.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[42:43]:
        PLAYER_CHAMBERS_OF_XERIC_CHALLENGE_MODE.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[43:44]:
        PLAYER_CHAOS_ELEMENTAL.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[44:45]:
        PLAYER_CHAOS_FANATIC.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[45:46]:
        PLAYER_COMMANDER_ZILYANA.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[46:47]:
        PLAYER_CORPOREAL_BEAST.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[47:48]:
        PLAYER_CRAZY_ARCHAEOLOGIST.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[48:49]:
        PLAYER_DAGANNOTH_PRIME.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[49:50]:
        PLAYER_DAGANNOTH_REX.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[50:51]:
        PLAYER_DAGANNOTH_SUPREME.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[51:52]:
        PLAYER_DERANGED_ARCHAEOLOGIST.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[52:53]:
        PLAYER_GENERAL_GRAARDOR.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[53:54]:
        PLAYER_GIANT_MOLE.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[54:55]:
        PLAYER_GROTESQUE_GUARDIANS.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[55:56]:
        PLAYER_HESPORI.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[56:57]:
        PLAYER_KALPHITE_QUEEN.append(skills[1])
        PLAYER_IND.append(skills[1]) 
        
    for skills in scores[57:58]:
        PLAYER_KING_BLACK_DRAGON.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[58:59]:
        PLAYER_KRAKEN.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[59:60]:
        PLAYER_KREEARRA.append(skills[1])
        PLAYER_IND.append(skills[1])

    for skills in scores[60:61]:
        PLAYER_KRIL_TSUTSAROTH.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[61:62]:
        PLAYER_MIMIC.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[62:63]:
        PLAYER_NIGHTMARE.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[63:64]:
        PLAYER_OBOR.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[64:65]:
        PLAYER_SARACHNIS.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[65:66]:
        PLAYER_SCORPIA.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[66:67]:
        PLAYER_SKOTIZO.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[67:68]:
        PLAYER_THE_GAUNTLET.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[68:70]:
        PLAYER_THE_CORRUPTED_GAUNTLET.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[70:71]:
        PLAYER_THEATRE_OF_BLOOD.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[71:72]:
        PLAYER_THERMONUCLEAR_SMOKE_DEVIL.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[72:73]:
        PLAYER_TZKAL_ZUK.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[73:74]:
        PLAYER_TZTOK_JAD.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[74:75]:
        PLAYER_VENENATIS.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[75:76]:
        PLAYER_VETION.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[76:77]:
        PLAYER_VORKATH.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[77:78]:
        PLAYER_WINTERTODT.append(skills[1])
        PLAYER_IND.append(skills[1])

    for skills in scores[78:79]:
        PLAYER_ZALCANO.append(skills[1])
        PLAYER_IND.append(skills[1])
        
    for skills in scores[79:80]:
        PLAYER_ZULRAH.append(skills[1])
        PLAYER_IND.append(skills[1])        
        
#######################################################################################    

PLAYER_TRUE = PLAYER_IND

PIfile = "PIfile"
pickle.dump(PLAYER_IND,open(PIfile,"wb"))

print(PLAYER_IND[0])
print(PLAYER_NAME[0])

MAX_VAL = np.amax(PLAYER_IND)
MIN_VAL = np.amin(PLAYER_IND)


print("Premax value:",MAX_VAL)
print("Premin value:",MIN_VAL)
print("Post shape: ",np.shape(PLAYER_IND))


PLAYER_IND = np.reshape(PLAYER_IND,(-1,79)) #take this below scaler to fix everything lol
print("Final shape: ",np.shape(PLAYER_IND))
########################################### DATA SCALE AND NORMALIZE [ENTRIES/78]

transformer = Normalizer(norm ='l2')
PLAYER_IND = transformer.fit_transform(PLAYER_IND)

########################################### 
MAX_VAL = np.amax(PLAYER_IND)
MIN_VAL = np.amin(PLAYER_IND)
print("Postmax value:",MAX_VAL)
print("Postmin value:",MIN_VAL)

print(PLAYER_IND[0])
print(PLAYER_NAME[0])

print(np.shape(PLAYERDATA))


# In[2]:


n_clusters = 300
kmeans = KMeans(n_clusters, init='k-means++') 
kmeans.fit(PLAYER_IND)
clusters = kmeans.cluster_centers_
y_km = kmeans.fit_predict(PLAYER_IND)

score = sklearn.metrics.silhouette_score(PLAYER_IND, kmeans.labels_, metric='euclidean')
metascore = sklearn.metrics.silhouette_samples(PLAYER_IND, kmeans.labels_, metric='euclidean')

print("Clusters:",clusters)
print("y_km:",y_km)
print("Entries:",len(y_km))
print('Silhouetter Score: %.3f' % score)
print("Metascores:",len(metascore))
print("Metascore Values:")
print(metascore)

MAX_metascore = np.amax(metascore)
MIN_metascore = np.amin(metascore)
print("Max Metascore Value:"+str(MAX_metascore))
print("Min Metascore Value:"+str(MIN_metascore))


# In[4]:


np.shape(PLAYER_IND) #features
np.shape(y_km) #labels

XX_train, XX_test, yy_train, yy_test = train_test_split(PLAYER_IND, y_km, test_size=0.1)

knn = KNeighborsClassifier(n_neighbors=5, weights='distance', algorithm='brute')
knn.fit(XX_train,yy_train)
yy_pred = knn.predict(XX_test)

print("Accuracy:",metrics.accuracy_score(yy_test, yy_pred))

############## PLAYER LOOKUP #################

name = "Ferrariic"
namemod = name+"\n"

ind = PLAYER_NAME.index(namemod)

player_predict = knn.predict(PLAYER_IND[ind].reshape(1,-1))
player_predprob = knn.predict_proba(PLAYER_IND[ind].reshape(1,-1))
print("Predicted group: ", player_predict)
print(player_predprob)
print(PLAYER_IND[ind].reshape(1,-1))
print(y_km[ind])
print(PLAYER_NAME[ind])
print(ind)

knnfile = "OSRS_KNN_V1"
ykmfile = "ykmfile"
traindata = "traindata"
pnamefile = "pnamefile"

pickle.dump(knn,open(knnfile,"wb"))
pickle.dump(y_km,open(ykmfile,"wb"))
pickle.dump(PLAYER_IND,open(traindata,"wb"))
pickle.dump(PLAYER_NAME,open(pnamefile,"wb"))


# In[ ]:


osrsknn = pickle.load(open("OSRS_KNN_V1","rb")) #LOAD PROGRAM
osrsknn_predict = osrsknn.predict(PLAYER_IND[2].reshape(1,-1))
print(osrsknn_predict)
print(y_km[2])

