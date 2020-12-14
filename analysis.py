import numpy as np
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join
import model_building as model


# correlation trace computation as improved by StackOverflow community
# O - matrix of observed leakage (i.e. traces)
# P - column of prediction
# returns a correlation trace
def corr_coeff(O, P):
    n = P.size
    DO = O - (np.einsum('ij->j', O, dtype='float64') / np.double(n))
    DP = P - (np.einsum('i->', P, dtype='float64') / np.double(n))
    tmp = np.einsum('ij,ij->j', DO, DO)
    tmp *= np.einsum('i,i->', DP, DP)
    tmp = np.dot(DP, DO) / np.sqrt(tmp)
    return tmp



def plot_corr(X,y):
    corr = corr_coeff(X,y)
    plt.plot(corr)
    plt.xlabel('Points in time')
    plt.ylabel('Correlation')


def analyse_AES(mypath):
    byte = 0
    measure, plaintext = load_all_data(mypath)
    y = model.aes_sbox_model(plaintext,byte)
    plot_corr(measure,y)


def load_all_data(mypath):
    measure = []
    plaintext = []
    for f in listdir(mypath):
        if isfile(join(mypath, f)):
            measure.append(unPackdata(f))
            text = f[4:20]
            text_int= [ord(t) for t in text] # TODO: how to convert to int???
            plaintext.append(text_int)
    
    return measure,plaintext

