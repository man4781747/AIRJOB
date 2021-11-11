import base64

def enctry(s):
    k = '9h000AkiraChen'
    encry_str = ""
    for i,j in zip(s,k): 
        temp = str(ord(i)+ord(j))+'_' 
        encry_str = encry_str + temp
    s1 = base64.b64encode(encry_str.encode("utf-8"))
    return s1.decode('utf-8')

def dectry(s2):
    s2 = s2.encode("utf-8")
    p = base64.b64decode(s2).decode("utf-8")
    k = '9h000AkiraChen'
    dec_str = ""
    for i,j in zip(p.split("_")[:-1],k): 
        temp = chr(int(i) - ord(j))
        dec_str = dec_str+temp
    return dec_str
	