import numpy as np
import ujson as json
import time

img = (65535*np.random.rand(4656*3520)).astype(int)

print(img.shape)

d = { 'Value': img.tolist()}

ts=time.time()
j= json.dumps(d)
te=time.time()
print(f'Serialization took {te-ts} seconds')
print(len(j))

f=open('pyimg_test.json', 'w')
f.write(j+'\n')
f.close()

f=open('pyimg_test.json', 'r')
r = json.load(f)
print(len(r['Value']))
print(type(r['Value']))
