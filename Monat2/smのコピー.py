
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 14:25:31 2017

@author: Liwen 
"""

import numpy as np  
from rrc import rrcfilter
from sender import sender
from receiver import receiver
import test
from f_sync import ML_approx_known, ML_unknown, ML_approx_unknown
import time
from commpy.utilities import bitarray2dec 
import matplotlib.pyplot as plt  


SNR_dB=30
#number of sender antennas
SA=4
#number of receiver antennas
RA=4
#data bits modulation order (BPSK)
M=2
mpsk_map=np.array([1,-1])
#mpsk_map =1/np.sqrt(2) * np.array([1+1j, -1+1j, 1-1j, -1-1j], dtype=complex)
#number of symbols
N=200
#number of training symbols
N_known=50
#symbol duration
T=1*1e-6
#Frequency offset
f_off=np.random.randint(0,1*1e-2/T)
print("f_off=",f_off)
#symbol offset 
#n_off=2
#phase offset
phi_off=np.random.random()*2*np.pi
phi_off=0
#number of Index bits per symbol
Ni=int(np.log2(SA))
#number of Data bits per symbol
Nd=int(np.log2(M))
#Upsampling rate
n_up=1
# RRC Filter (L=K * sps + 1, sps, t_symbol, rho)
filter_=rrcfilter(8*n_up+1,n_up , 1,0)

#Channel matrix
H=1/np.sqrt(2)*((np.random.randn(RA,SA))+1j/np.sqrt(2)*(np.random.randn(RA,SA)))
#H=np.ones([RA,SA])

#sender
sender_=sender(N,N_known,Ni,Nd,mpsk_map,filter_)
print("n_start=",sender_.n_start)
#training symbols(/bits) which may be shared with receiver, when a data-aided method is used
symbols_known=sender_.symbols_known
ibits=sender_.ibits
dbits=sender_.dbits
ibits_known=sender_.ibits_known
dbits_known=sender_.dbits_known
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#with Filter(noch zu bearbeiten,überabtastung!)
receiver_=receiver(H,sender_,SNR_dB,filter_,mpsk_map)
r=receiver_.channel()
r_mf=receiver_.r_mf

yi,yd=receiver_.detector(r_mf,H)
BERi_0,BERd_0=test.BER(yi,yd,Ni,Nd,ibits,dbits)


#with offsets
#Frequency offset before MF(+filter length)
#off=np.exp(1j*2*np.pi*f_off*np.arange(sender_.bbsignal().size)*T/filter_.n_up)
#r=receiver_.channel()*np.repeat(off,RA).reshape([-1,RA])
#r_mf=receiver_.Matched_Filter(r.real)+1j*receiver_.Matched_Filter(r.imag)
#offset after MF

#r=receiver_.channel()
#r_mf=receiver_.Matched_Filter(r.real)+1j*receiver_.Matched_Filter(r.imag)
off=np.exp(1j*2*np.pi*f_off*np.arange(r_mf.shape[0])*T/filter_.n_up)

#
r_off_ft=r_mf*np.repeat(off,RA).reshape([-1,RA])*np.exp(1j*phi_off)
#r_off_ft=np.concatenate((r_off_f[n_off:],r_off_f[:n_off]))*np.exp(1j*2*np.pi*phi_off)


    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#### Frequency estimation without n_offset
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
##Frequency offset estimation with ML-Approximation(data-aided) with known channel for each antenna
##f_est=ML_approx_known(r_off_ft,T,symbols,ibits,H)
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##ML with channel unknown
##f_est1=ML_unknown(r_off_f,T,symbols,ibits)
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##ML_approx with channel unknown
#f_est1=ML_approx_unknown(r_off_ft[sender_.n_start:sender_.n_start+N_known],T,symbols_known,ibits_known)
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
###Channel Estimation
##H_est=np.zeros([RA,SA],complex)  
##index=bitarray2dec(ibits)
##i=np.zeros(SA)
##for k in range(0,symbols.size):
##    H_est[:,index[k]]+= r[k,:]/symbols[k]*np.exp(-1j*2*np.pi*T*f_est*k)
##    i[index[k]]=i[index[k]]+1
###Anzahl soll auf Anzahl der Benutzung von jeder Sendeantenne angepasst werden
##H_est=H_est/np.repeat(i,RA).reshape(-1,RA).transpose()
##H_diff=H-H_est
#

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##speed test
##t1=time.clock()
##t=time.clock()-t1
#


    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#coarse Estimation for f_off
f_off_coarse=f_off*0.8
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#coarse synchronisation for f_off
off_syc=np.exp(-1j*2*np.pi*f_off_coarse*np.arange(r_mf.shape[0])*T/filter_.n_up)
r_syc_coarse=r_off_ft*np.repeat(off_syc,RA).reshape([-1,RA])
print(f_off-f_off_coarse)

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#Joint Estimation for f_off,n_start and CSI 
n_range=N-N_known
L=np.zeros(n_range-1)
#when n=0 function doesn't work,this situation should be tested by a if command
index=bitarray2dec(ibits_known)
for n in range(1,n_range):   
    f_estt=ML_approx_unknown(r_syc_coarse[n:n+N_known],T,symbols_known,ibits_known)
    H_est=np.zeros([RA,SA],complex)  
    i=np.zeros(SA)
    #Channel estimation
    r=r_syc_coarse[n:n+N_known+1]
    for k in range(0,symbols_known.size):
        H_est[:,index[k]]+= r[k,:]/symbols_known[k]*np.exp(-1j*2*np.pi*T*f_estt*(k+n))
        i[index[k]]=i[index[k]]+1
    #Anzahl soll auf Anzahl der Benutzung von jeder Sendeantenne angepasst werden
    H_est=H_est/np.repeat(i,RA).reshape(-1,RA).transpose()
   
    #Likelihood function for Timing estimation       
    for m in range(0,symbols_known.size):
        L[n-1]+=np.linalg.norm(r[m,:]-H_est[:,index[m]]*np.exp(1j*2*np.pi*T*m)*symbols_known[m])**2
    n_est=np.argmin(L)+1   

r=r_syc_coarse[n_est:n_est+N_known]

##one more estimation after estimation for n (or save Estimation results for each n ?
f_est=ML_approx_unknown(r,T,symbols_known,ibits_known)
H_est=np.zeros([RA,SA],complex) 
i=np.zeros(SA)
for k in range(0,symbols_known.size):
    H_est[:,index[k]]+= r[k,:]/symbols_known[k]*np.exp(-1j*2*np.pi*T*f_est*(k+n_est))
    i[index[k]]=i[index[k]]+1
H_est=H_est/np.repeat(i,RA).reshape(-1,RA).transpose()

#
#    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#Frequency synchronisation
off_syc=np.exp(-1j*2*np.pi*f_est*(np.arange(r_mf.shape[0]))*T)
r_f_syc=r_syc_coarse*np.repeat(off_syc,RA).reshape([-1,RA])

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##Test for the Joint estimation
yi,yd=receiver_.detector(r_f_syc,H_est)
#yi,yd=rr.detector(H_est,SNR_dB,mpsk_map,r_ft_syc)
BERi,BERd=test.BER(yi,yd,Ni,Nd,ibits,dbits)


#
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
print("f_est=",f_est,", n_est=",n_est," , H_diff_max=", np.max(H-H_est))  
print("BER for index bits=",BERi,", BER for data bits=",BERd)  
##







