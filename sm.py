#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 14:25:31 2017

@author: Liwen 
"""

import numpy as np  
from rrc import rrcfilter
from sender_class import sender
from receiver_class import receiver
import f_sync as fr
from f_sync import ML_approx_known, NDA, ML_unknown, ML_approx_unknown
import time
from commpy.utilities import bitarray2dec 
#def sm(SNR_noise_dB,SNR_RA_dB,f_off):
SNR_noise_dB=50
SNR_RA_dB=0
SA=4
#number of sender antennas
RA=16
#number of receiver antennas
M=2
#data bits modulation order (BPSK)
mpsk_map=np.array([1,-1])
#mpsk_map =1/np.sqrt(2) * np.array([1+1j, -1+1j, 1-1j, -1-1j], dtype=complex)
N=30
#number of symbols
T=1*1e-5
#symbol duration
f_off=51
n_off=0
phi_off=0
#number of training symbols
Ni=int(np.log2(SA))
#number of Index bits per symbol
Nd=int(np.log2(M))
#number of Data bits per symbol
filter_=rrcfilter(8*1+1,1 , 1,0)
# RRC Filter (L=K * sps + 1, sps, t_symbol, rho)
#???? BER fuer Index verschlechtet sich bei Uebungabtastung
# besser mit rho=1
H=1/np.sqrt(2)*((np.random.randn(RA,SA))+1j/np.sqrt(2)*(np.random.randn(RA,SA)))
#H=np.abs(H)
#Channel matrix
#H=np.ones([RA,SA])  

sender_=sender(N,Ni,Nd,mpsk_map,filter_)
#tx
s=sender_.bbsignal()
#r_off=s

#training symbols(/bits) which may be shared with receiver, when a data-aided method is used
symbols=sender_.symbols
ibits=sender_.ibits


receiver_=receiver(H,sender_,s,SNR_noise_dB,SNR_RA_dB,filter_,mpsk_map)
r=receiver_.channel()
r_mf=receiver_.Matched_Filter(r.real)+1j*receiver_.Matched_Filter(r.imag)
BERi,BERd=receiver_.BER()

#with frequency offset
off=np.exp(1j*2*np.pi*f_off*np.arange(sender_.bbsignal().size)*T/filter_.n_up)
r=receiver_.channel()*np.repeat(off,RA).reshape([-1,RA])
r_mf=receiver_.Matched_Filter(r.real)+1j*receiver_.Matched_Filter(r.imag)
r_mf=r_mf[n_off:]*np.exp(1j*2*np.pi*phi_off)




#sps=filter_.n_up
##r_sync=np.zeros([r_mf.shape[0],r_mf.shape[1]-1])
#def rint(x):
#    return np.int(np.round(x))
#
#class gardner_timing_recovery:
#    e = [0]
#    gamma = 1e-1
#    tau = [0, 0]
#    output_symbols = []
#    
#    def run(self, y):
#        for k in range(y.size//sps - 1):
#            self.output_symbols.append(y[k*sps + rint(self.tau[k])])
#            if k > 0:
#                self.e.append(self.TED(y, k))  # update error signal
#                self.tau.append(self.loop_filter(k))
#    
#    def TED(self, y, k):
#        return (y[(k-1)*sps + self.rint(self.tau[k-1])] - y[k*sps + rint(self.tau[k])]) * y[k * sps - sps//2 + rint(self.tau[k-1])]
#    
#    def loop_filter(self, k):
#        return self.tau[k] + self.gamma * self.e[k]
#    
#    def rint(self, x):
#        return int(round(x))
##
#timing_sync = gardner_timing_recovery()
#timing_sync.run(r_mf[:,1])
#r_sync = timing_sync.output_symbols
#    #timing_sync.run(r[i,:])
#    #r_sync[i,:] = timing_sync.output_symbols
    







#t1=time.clock()
#Frequency offset estimation with ML-Approximation(data-aided) with known channel
#f_est=ML_approx1(r_mf,T,symbols,ibits,H)

#ML with channel unknown
#f_est=ML_unknown(r_mf,T,symbols,ibits)

#ML_approx with channel unknown
f_est=ML_approx_unknown(r_mf,T,symbols,ibits)


##Frequency offset estimation with Non-Data-Aided method based on MPSK
#f_of=NDA(r_mf,M,T,H)
#r_of= np.repeat(r_mf,H.shape[1]).reshape([N,RA,SA])
#t=time.clock()-t1




print(f_est)    








