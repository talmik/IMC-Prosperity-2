# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from scipy.optimize import curve_fit
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import math
 
df = pd.read_csv('/Users/jamie/Desktop/comp1730/IMC/round-1-island-data-bottle/prices_round_1_day_0.csv',sep =';')

df = df[df['product']=='STARFRUIT']
time = list(df['timestamp'])
price = list(df['mid_price'])
# sine, it seems to hover around 5000, with amplitude 60

def f(x,A,b,phi,c):
    y = A*np.sin(b*x+phi)+c
    return y

initial = (40,2*math.pi/1000000,math.pi ,5050)

popt, pcov = curve_fit(f,time,price, initial)
print(popt)

time_array=np.array(time)

plt.scatter(time,price)
plt.plot(time_array, f(time_array, *popt))

#initial = (amplitude, angular frequency, phase, shift)