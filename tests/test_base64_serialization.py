import numpy as np
import base64
import time

img = (65535*np.random.rand(4656*3520)).astype(np.int16)

print(img.shape)

ts=time.time()
b = base64.b64encode(img)
te=time.time()
print(f'b64encode took {te-ts} seconds')
print(len(b))

f=open('pyimg_test.b64', 'wb')
f.write(b)
f.close()

f=open('pyimg_test.b64', 'rb')
fb = f.read()
print(f'Length of read data is {len(fb)}')
f.close()
ts=time.time()
decoded = base64.b64decode(fb)
read_img = np.frombuffer(decoded, dtype=np.int16)
te=time.time()
print(f'b64decode took {te-ts} seconds')
print(len(read_img))
print(type(read_img))

print(np.array_equal(img, read_img))
