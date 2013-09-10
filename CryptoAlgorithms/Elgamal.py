from Crypto import Random
from Crypto.Random import random
import CustomElgamal
from Crypto.PublicKey.pubkey import *
from Crypto.Util import number

def GetElgamalParamqp(bits = 100):
    while 1:
        q = bignum(getPrime(bits-1, Random.new().read))
        p = 2*q+1
        if number.isPrime(p, randfunc=Random.new().read):
            break
    return q,p

def _StringTolist(string,blocksize):
    blocknum = len(string) / blocksize
    for i in range(blocknum):
        yield string[:blocksize]
        string = string[blocksize:]
    yield string
    
def StringToList(string,blocksize = 12):
    return list(_StringTolist(string, blocksize))

def CompareStringList(stringlist1,stringlist2):
    len1 = len(stringlist1)
    len2 = len(stringlist2)
    if len1 != len2:
        return False
    for i in range(len1):
        if stringlist1[i] != stringlist2[i]:
            return False
    return True

def GetStructFmt(m):
    return "".join([str(len(m[i])) + "s" for i in range(len(m))])

class Elgamal:
    def __init__(self,q,p,bits = 100):
        self.__elgamalobject = CustomElgamal.generate(bits, q,p,Random.new().read)
        self.__getRandomk()
        
    def __getRandomk(self):
        while 1:
            k = random.StrongRandom().randint(1,self.__elgamalobject.p-1)
            if GCD(k,self.__elgamalobject.p-1)==1: break
        self.__k = k
    
    def __EncryptoList(self,stringlist):
        for string in stringlist:
            yield self.__elgamalobject.encrypt(string, self.__k)[1]
    def EncryptoList(self,stringlist):
        return list(self.__EncryptoList(stringlist))

if __name__ == '__main__':
    param = GetElgamalParamqp()
    e1 = Elgamal(*param)
    e2 = Elgamal(*param)
    
    
    m1 = e2.EncryptoList(StringToList("89412eee21b23cd8cdbd3b4aa79728763fcf7f6f"))
    s1 = e1.EncryptoList(m1)
    m2 = e1.EncryptoList(StringToList("89412eee21b23cd8cdbd3b4aa79728763fcf7f6f"))
    s2 = e2.EncryptoList(m2)
    
    import struct
    
    fmt = GetStructFmt(m2)
    s = struct.pack(fmt,*m2)
    
    
    