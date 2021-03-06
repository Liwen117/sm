#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 11:17:55 2017

@author: Liwen
"""


#optimal detector
import numpy as np
from commpy.utilities import dec2bitarray,bitarray2dec
from collections import Counter
class receiver():
    def __init__(self,H,sender_,SNR_dB,filter_,mapp):
        self.H=H
        #self.H_est=H_est
        self.ibits=sender_.ibits
        self.dbits=sender_.dbits
        self.Ni=sender_.Ni
        self.Nd=sender_.Nd
        self.s=sender_.bbsignal()
        self.symbols=sender_.only_upsampling()
        self.SNR_dB=SNR_dB
        self.MF_ir=filter_.ir()
        self.sps=filter_.n_up
        self.mapp=mapp
        self.channel()
        self.rr=self.Matched_Filter(self.r.real)
        self.ri=self.Matched_Filter(self.r.imag)
        self.r_mf=self.rr+1j*self.ri
        #self.detector(self.r_mf)
      
#index fuer group delay waehlen, zusammen nach MF loeschen         
    def channel(self):
        noise_variance_linear = 10**(-self.SNR_dB / 10)
        s_a_index=np.repeat(bitarray2dec(self.ibits),self.sps)
        #turn index bits to the Antenne index 
         
        group_delay = (self.MF_ir.size - 1) // 2
        c=s_a_index[0:group_delay]
        d=s_a_index[-group_delay:]
#?      c=np.zeros(group_delay)

        s_a_index=np.concatenate((c,s_a_index,d))
        self.index=s_a_index
        r=np.zeros((self.s.size,self.H.shape[0]),complex)
        #initiate received signal in Bandpass
        for j in range(0,self.H.shape[0]):
            for i in range(0,s_a_index.size):
                n = np.sqrt(noise_variance_linear / 2) * (np.random.randn(self.s.size)+1j*np.random.randn(self.s.size) )
                r[i,j]=self.s[i]*self.H[j,s_a_index[i]]
                r[:,j]=r[:,j]+n
        self.r=r
        return r
    def channel_nf(self,n_up):
        noise_variance_linear = 10**(-self.SNR_dB / 10)
        s_a_index=np.repeat(bitarray2dec(self.ibits),n_up)
        rx=np.zeros((self.symbols.size,self.H.shape[0]),complex)
        for j in range(0,self.H.shape[0]):
            for i in range(0,s_a_index.size):
                n = np.sqrt(noise_variance_linear / 2) * (np.random.randn(self.symbols.size)+1j*np.random.randn(self.symbols.size) )
                rx[i,j]=self.symbols[i]*self.H[j,s_a_index[i]]
                rx[:,j]=rx[:,j]+n
        return rx
    
    def Matched_Filter(self,r_BB):
        group_delay = (self.MF_ir.size - 1) // 2
        r=np.zeros((len(r_BB)-self.MF_ir.size+1,r_BB.shape[1]),complex)
        #for each receiver-antenne
        for i in range(0,r_BB.shape[1]):
            a= np.convolve(self.MF_ir, r_BB[:,i])
            r[:,i] = a[ 2*group_delay: - 2*group_delay]
        #without downsampling
        #return r
        #with downsampling
        r_down = r[::self.sps]
        return r_down
    
# mit ueberabtastung steigt BER fuer index bits? Irgendwo falsch?     
# vor der Sendung group delay von dem Senderfilter loeschen,kein Indexauswahr
# nach MF noch mal group delay loeschen                
#    def channel(self):
#        noise_variance_linear = 10**(-self.SNR_noise_dB / 10)
#        s_a_index=np.repeat(bitarray2dec(self.ibits),self.sps)
#        #turn index bits to the Antenne index 
#         
#        group_delay = (self.MF_ir.size - 1) // 2
#        self.s=self.s[group_delay:-group_delay]
#        #c=s_a_index[0:group_delay]
#        #d=s_a_index[-group_delay:]
##?      c=np.zeros(group_delay)
#
#        #s_a_index=np.concatenate((c,s_a_index,d))
#        self.index=s_a_index
#        r=np.zeros((self.s.size,self.H.shape[0]),complex)
#        #initiate received signal in Bandpass
#        for j in range(0,self.H.shape[0]):
#            for i in range(0,s_a_index.size):
#                n = np.sqrt(noise_variance_linear / 2) * (np.random.randn(self.s.size)+1j*np.random.randn(self.s.size) )
#                r[i,j]=self.s[i]*self.H[j,s_a_index[i]]
#                r[:,j]=r[:,j]+n
#        self.r=r
#    
#
#    def Matched_Filter(self,r_BB):
#        group_delay = (self.MF_ir.size - 1) // 2
#        r=np.zeros((len(r_BB),r_BB.shape[1]),complex)
#        for i in range(0,r_BB.shape[1]):
#            a= np.convolve(self.MF_ir, r_BB[:,i])
#            r[:,i] = a[ 1*group_delay: - 1*group_delay]
#        r_down = r[::self.sps]
#        self.r_d=r_down
#        return r_down



 
    def detector(self,r,H_est):
        n=H_est.shape[1]
        g=np.zeros((n,self.mapp.size,r.shape[0]),complex)
        yi=np.zeros(r.shape[0])
        yd=np.zeros(r.shape[0])
        yi_=np.zeros(r.shape[0]//self.sps)
        yd_=np.zeros(r.shape[0]//self.sps)
        for i in range(0,r.shape[0]):
            #i.th symbol
            for j in range(0,n):
                #which sender
                for q in range(0,self.mapp.size):
                    #which datasymbol
                    g[j,q,i]=np.linalg.norm(H_est[:,j]*self.mapp[q])**2-2*np.real(np.dot(np.conj(r[i]),H_est[:,j]*self.mapp[q]))
            yi[i],yd[i]=np.unravel_index(np.argmin(g[:,:,i]), (n,self.mapp.size))
        if self.sps!=1:    
            yii=yi.reshape([-1,self.sps])
            ydd=yd.reshape([-1,self.sps])               
            for i in range(0,yii.shape[0]):
                yi_[i]=[fr for fr,nr in Counter(yii[i]).most_common(1)][0]
                yd_[i]=[fr for fr,nr in Counter(ydd[i]).most_common(1)][0]
        else:
            yi_=yi
            yd_=yd
        self.yi=yi
        self.yd=yd
        self.g=g
        return yi_,yd_
#    
    
#def BER(self):
#    xi=np.zeros((self.yi.size,self.Ni))
#    xd=np.zeros((self.yd.size,self.Nd))
#    for i in range(0,self.yi.size):
#        xi[i]=dec2bitarray(int(self.yi[i]),self.Ni)
#    beri=np.sum(np.not_equal(xi.reshape((1,-1)),np.matrix(self.ibits).H.reshape((1,-1))))/xi.size 
#    for i in range(0,self.yd.size):
#        xd[i]=dec2bitarray(int(self.yd[i]),self.Nd)
#    berd=np.sum(np.not_equal(xd.reshape((1,-1)),np.matrix(self.dbits).H.reshape((1,-1))))/xd.size 
#    return beri, berd
    #    def dmixer(r_BP,fc,fs):
#        t = np.arange(len(r_BP)) / fs
#        cos = np.sqrt(2) * np.cos(2 * np.pi * fc * t)
#        sin = np.sqrt(2) * np.sin(2 * np.pi * fc * t)
#        r_BBr=np.zeros(r_BP.shape)
#        r_BBi=np.zeros(r_BP.shape)
#        for i in range(0,r_BP.shape[1]):
#            r_BBr[:,i]=r_BP[:,i] * cos 
#            r_BBi[:,i]=r_BP[:,i] * (-sin)
#        return r_BBr,r_BBi

#
#def detector(H,mapp,r):
#    n=H.shape[1]
#    g=np.zeros((n,mapp.size,r.shape[0]),complex)
#    yi=np.zeros(r.shape[0])
#    yd=np.zeros(r.shape[0])
#    for i in range(0,r.shape[0]):
#        #per symbol
#        for j in range(0,n):
#            #which sender
#            for q in range(0,mapp.size):
#                #which datasymbol
#                g[j,q,i]=np.linalg.norm(H[:,j]*mapp[q])**2-2*np.real(r[i]@H[:,j]*mapp[q])
#        yi[i],yd[i]=np.unravel_index(np.argmin(g[:,:,i]), (n,mapp.size))
#        return yi,yd

   