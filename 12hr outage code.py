#Code to delete all data from Fri 1 7:30pm onwards ready for power outage delay(s) to be inserted
import numpy as np
import pandas as pd
import xlrd
import csv
from random import randrange
import os
import glob


#load in all the houses at once
path = os.getcwd()
csv_files = glob.glob(os.path.join(path, "*.csv"))

#put all these .csv house data files into a dictionary
house_input_dict = {}
for i, f in zip(range(84), csv_files):
    df = pd.read_csv(f)
    x = f.split("\\")[-1]
    id = x.split(".")[0]
    new = {id:df}
    house_input_dict.update(new)
    print(id)

print(house_input_dict)

#deleting the data from 'Charging Energy', 'Charging Power', and 'State of Charge (%)' columns
for house in house_input_dict.keys():
    HouseData = house_input_dict[house]
    print('Data for', house, 'loaded in')
    #print(HouseData)
    #firstly delete data on Fri 1 after 7:30pm (start of the outage)
    for i in range(40, 48):
        #print(i)
        HouseData["Fri2 Charging Energy"][i] = 0
        HouseData["Fri2 Charging Power"][i] = 0
        if HouseData["Fri2 Energy"][i] == HouseData["Fri2 Energy"][i-1]:
            HouseData["Fri2 Battery Capacity"][i] = HouseData["Fri2 Battery Capacity"][i-1]
        else:
            HouseData["Fri2 Battery Capacity"][i] = HouseData["Fri2 Battery Capacity"][i] - (HouseData["Fri2 Energy"][i]-HouseData["Fri2 Energy"][i-1])
        HouseData["Fri2 State of Charge (%)"][i] = (HouseData["Fri2 Battery Capacity"][i]/37)*100
        #print('Here')
    #delete data going into saturday (end of the outage - 12hrs till 07:30AM)
    for i in range (0, 16):
        HouseData["Sat2 Charging Energy"][i] = 0
        HouseData["Sat2 Charging Power"][i] = 0
    HouseData["Sat2 Battery Capacity"][0] = HouseData["Fri2 Battery Capacity"][47]
    #HouseData["Sat2 State of Charge (%)"][0] = HouseData["Fri2 State of Charge (%)"][47]
    for i in range (1,48):
        HouseData['Sat2 Battery Capacity'][i] = np.nan
        #HouseData["Sat2 State of Charge (%)"][i] = np.nan

    #Economy tariffs only charge between 00:00 and 07:00 so when the power comes back on at
    #07:30am then no cars will ever start charging, will all have to wait till midnight

    #complete Sat1
    for i in range(1, 48):
        HouseData['Sat2 Battery Capacity'][i] = HouseData['Sat2 Battery Capacity'][0]-HouseData['Sat2 Energy'][i]

    for i in range (0, 48):
        HouseData['Sat2 State of Charge (%)'][i] = (HouseData['Sat2 Battery Capacity'][i]/37)*100

    #delete Sun1's battery capacity, state of charge, charging energy and charging power columns as these will all change

    for i in range (0,48):
        HouseData['Sun2 Battery Capacity'][i] = np.nan
        HouseData["Sun2 State of Charge (%)"][i] = np.nan
        HouseData['Sun2 Charging Energy'][i] = np.nan
        HouseData['Sun2 Charging Power'][i] = np.nan

    #first line of Sun1 inputted - ready for for loops to continue the way
    HouseData['Sun2 Battery Capacity'][0] = HouseData['Sat2 Battery Capacity'][47]
    HouseData['Sun2 State of Charge (%)'][0] = HouseData['Sat2 State of Charge (%)'][47]
    HouseData['Sun2 Charging Energy'][0] = 0 #the reading at midnigt itself will always be zero
    HouseData['Sun2 Charging Power'][0] = 0 #the reading at midnigt itself will always be zero

    #delete these four columns for Mon2
    for i in range (0,48):
        HouseData['Mon3 Battery Capacity'][i] = np.nan
        HouseData["Mon3 State of Charge (%)"][i] = np.nan
        HouseData['Mon3 Charging Energy'][i] = np.nan
        HouseData['Mon3 Charging Power'][i] = np.nan

    #for a 12hr power outage, the impact should be alleviate after just a couple
    #of days charging back up opportunities, so from tues2 onwards, dont need to delete anything?

    #first time charging again after power outage - sun1
    if HouseData['Sun2 Battery Capacity'][0] < 0.8*37: #less than 80%
        if HouseData['Sun2 Location Code'][1] == 0:
            HouseData['Sun2 Charging Power'][1] = 6.6
            HouseData['Sun2 Charging Energy'][1] = 3.3
            HouseData['Sun2 Battery Capacity'][1] = HouseData['Sun2 Battery Capacity'][0] + 3.3
            #HouseData['Sun2 State of Charge (%)'][1] = (HouseData['Sun2 Battery Capacity'][1]/37)*100

    for i in range(2, 15):
        if HouseData['Sun2 Location Code'][i] == 0: #check car is at home still
            if HouseData['Sun2 Battery Capacity'][i-1] < 0.8*37: #less than 80%
                HouseData['Sun2 Charging Power'][i] = 6.6
                HouseData['Sun2 Charging Energy'][i] = 3.3
                HouseData['Sun2 Battery Capacity'][i] = HouseData['Sun2 Battery Capacity'][i-1] + 3.3
                #HouseData['Sun2 State of Charge (%)'][i] = (HouseData['Sun2 Battery Capacity'][i]/37)*100
                if HouseData['Sun2 Battery Capacity'][i] > 0.8*37:
                    delta = HouseData['Sun2 Battery Capacity'][i] - 29.6
                    HouseData['Sun2 Battery Capacity'][i] = 29.6
                    HouseData['Sun2 Charging Energy'][i] = 3.3 - delta
            else:
                HouseData['Sun2 Battery Capacity'][i] = HouseData['Sun2 Battery Capacity'][i-1]
                HouseData['Sun2 Charging Power'][i] = 0
                HouseData['Sun2 Charging Energy'][i] = 0
        else:
            #leave = HouseData['Sun2 Battery Capacity'][i-1] #leave is the battery charge when the car leaves home
            HouseData['Sun2 Battery Capacity'][i] = HouseData['Sun2 Battery Capacity'][i-1] - (HouseData['Sun2 Energy'][i] - HouseData['Sun2 Energy'][i-1])
            HouseData['Sun2 Charging Power'][i] = 0
            HouseData['Sun2 Charging Energy'][i] = 0
            #HouseData['Sun2 State of Charge (%)'][i] = (HouseData['Sun2 Battery Capacity'][i]/37)*100

    #filling in rest of Sunday
    for i in range(15, 48):
        HouseData['Sun2 Battery Capacity'][i] = HouseData['Sun2 Battery Capacity'][i-1] - (HouseData['Sun2 Energy'][i] - HouseData['Sun2 Energy'][i-1])
        HouseData['Sun2 Charging Power'][i] = 0
        HouseData['Sun2 Charging Energy'][i] = 0

    for i in range(0, 48):
        HouseData['Sun2 State of Charge (%)'][i] = (HouseData['Sun2 Battery Capacity'][i]/37)*100

    #start of mon2 values
    HouseData['Mon3 Battery Capacity'][0] = HouseData['Sun2 Battery Capacity'][47]
    HouseData['Mon3 State of Charge (%)'][0] = HouseData['Sun2 State of Charge (%)'][47]
    HouseData['Mon3 Charging Power'][0] = 0
    HouseData['Mon3 Charging Energy'][0] = 0

    #charging for mon2
    if HouseData['Mon3 Battery Capacity'][0] < 0.8*37: #less than 80%
        if HouseData['Mon3 Location Code'][1] == 0:
            HouseData['Mon3 Charging Power'][1] = 6.6
            HouseData['Mon3 Charging Energy'][1] = 3.3
            HouseData['Mon3 Battery Capacity'][1] = HouseData['Mon3 Battery Capacity'][0] + 3.3
            #HouseData['Mon3 State of Charge (%)'][1] = (HouseData['Mon3 Battery Capacity'][1]/37)*100
    else:
        if HouseData['Mon3 Battery Capacity'][0] == 29.6:
            HouseData['Mon3 Charging Power'][1] = 0
            HouseData['Mon3 Charging Energy'][1] = 0
            HouseData['Mon3 Battery Capacity'][1] = 29.6

    for i in range(2, 15):
        if HouseData['Mon3 Battery Capacity'][i-1] < 0.8*37: #less than 80%
            if HouseData['Mon3 Location Code'][i] == 0: #check car is at home still
                HouseData['Mon3 Charging Power'][i] = 6.6
                HouseData['Mon3 Charging Energy'][i] = 3.3
                HouseData['Mon3 Battery Capacity'][i] = HouseData['Mon3 Battery Capacity'][i-1] + 3.3
                #HouseData['Mon3 State of Charge (%)'][i] = (HouseData['Mon3 Battery Capacity'][i]/37)*100
                if HouseData['Mon3 Battery Capacity'][i] > 0.8*37:
                    delta = HouseData['Mon3 Battery Capacity'][i] - 29.6
                    HouseData['Mon3 Battery Capacity'][i] = 29.6
                    HouseData['Mon3 Charging Energy'][i] = 3.3 - delta
            else:
                HouseData['Mon3 Battery Capacity'][i] = HouseData['Mon3 Battery Capacity'][i-1]
                HouseData['Mon3 Charging Power'][i] = 0
                HouseData['Mon3 Charging Energy'][i] = 0
        else:
            HouseData['Mon3 Battery Capacity'][i] = 29.6
            HouseData['Mon3 Charging Power'][i] = 0
            HouseData['Mon3 Charging Energy'][i] = 0
            #HouseData['Mon3 State of Charge (%)'][i] = (HouseData['Mon3 Battery Capacity'][i]/37)*100

    #fill in rest on Mon2
    for i in range(15, 48):
        HouseData['Mon3 Battery Capacity'][i] = 29.6 - HouseData['Mon3 Energy'][i]
        #HouseData['Mon3 State of Charge (%)'][i] = (HouseData['Mon3 Battery Capacity'][i]/37)*100
        HouseData['Mon3 Charging Power'][i] = 0
        HouseData['Mon3 Charging Energy'][i] = 0

    for i in range(0, 48):
        HouseData['Mon3 State of Charge (%)'][i] = (HouseData['Mon3 Battery Capacity'][i]/37)*100


    #dynamic filesaving name and saving all results to a new folder on the desktop
    newpath = r'C:\Users\mckin\Desktop\12hr Power Outage (100 Econ)'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    HouseData.to_csv(r'C:\Users\mckin\Desktop\12hr Power Outage (100 Econ)\ '+str(house)+ '.csv')
    print(house, 'SAVED')
