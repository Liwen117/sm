#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 15:58:16 2017

@author: lena
"""
import numpy as np
from commpy.utilities import dec2bitarray,bitarray2dec
def training_symbols(N,Nd,Ni):
#Ni=2
#Nd=2
#N=16
#    index=np.arange(0,2**Ni)
#    ibits=np.zeros([Ni,2**Ni])
#    for i in range(0,2**Ni):
#        ibits[:,i]=dec2bitarray(index[i],Ni)
#    #!!!!auf ML_approx_unknown Zeile 93 anpassen!!
#    ibits_=ibits
#    for j in range(1,N//(2**Ni)):
#        ibits=np.concatenate((ibits_,ibits),1)
#        j=j+1
#    #ibits=np.transpose(ibits_).reshape([-1,1])
    ibits=np.random.choice([0,1],N*Ni).reshape((Ni,-1))
    #ibits=np.array([1,0,1,0,1,1,1,1,1,0,1,1,1,1,0,1,1,0,1,1,1,0,1,1]).reshape((2,-1))
    #ibits=np.array([0,0,1,0,1,0,1,1,1,1,1,1,0,1,1,1]).reshape((2,-1))
    #ibits=np.array([0,0,0,0,1,1,1,1,0,0,0,1,0,0,1,1]).reshape((2,-1))


#    ts=np.transpose([int(1),int(0)])
#    dbits=ts
#    for j in range(1,N//2//Nd):
#        dbits=np.concatenate((dbits,ts),0)
#        j=j+1
#    dbits=dbits.reshape((Nd,-1))
    dbits=np.random.choice([0,1],N*Nd).reshape((Nd,-1))
    #dbits=np.random.choice([1],N*Nd).reshape((Nd,-1))
    return ibits,dbits

ib,db=training_symbols(32,1,2)

    