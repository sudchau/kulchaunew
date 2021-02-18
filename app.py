from flask import Flask, render_template, request
from PIL import Image as im
import base64
import pytesseract
import io
import cv2
import numpy as np
from scipy.ndimage import interpolation as inter
app = Flask(__name__)

def find_score(arr, angle):
	data = inter.rotate(arr, angle, reshape=False, order=0)
	hist = np.sum(data, axis=1)
	score = np.sum((hist[1:] - hist[:-1]) ** 2)
	return hist, score

def main(img):
    img_raw=img
    wd, ht = img.size
    delta = 1
    limit = 5
    angles = np.arange(-limit, limit+delta, delta)
    scores = []
    for angle in angles:
        hist, score = find_score(img, angle)
        scores.append(score)
    best_score = max(scores)
    best_angle = angles[scores.index(best_score)]
    data = inter.rotate(img, best_angle, reshape=False, order=0)
    img = im.fromarray((data).astype("uint8"))
    # img.save('skew_corrected.png')
    # img1 = cv2.imread(img,0)
    img1 = np.array(img)
    img1 = img1[:, :, ::-1].copy()
    img1_raw = img1
    img1 = cv2.medianBlur(img1,5)
    extractedInformation1 = pytesseract.image_to_string(img1)
    # img_raw.save('skew_corrected1.png')
    # img2 = cv2.imread('skew_corrected1.png',0)
    img2 = np.array(img_raw)
    img2 = img2[:,:,::-1].copy()
    img2_raw = img2
    img2 = cv2.medianBlur(img2,5)



    #img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    img3 = cv2.medianBlur(img1_raw,3)
    img4 = cv2.medianBlur(img2_raw,3)
    extractedInformation3 = pytesseract.image_to_string(img3)
    extractedInformation2 = pytesseract.image_to_string(img4)
    img5 = cv2.medianBlur(img1_raw,1) 
    img6 = cv2.medianBlur(img2_raw,1)
    extractedInformation4 = pytesseract.image_to_string(img5)
    extractedInformation5 = pytesseract.image_to_string(img6)
    extractedInformation6 = pytesseract.image_to_string(img2)
    extractedInformation  = str(extractedInformation1 + " " + extractedInformation2 + " " + extractedInformation3 + " " + extractedInformation4 + " " + extractedInformation5 + " " + extractedInformation6)
    n=len(extractedInformation)
    vote=0
    startvo=-1
    for i in range(n-10):
      c=0
      for j in range(10):
        if j<=2 and extractedInformation[i+j]>='A' and extractedInformation[i+j]<='Z':
          c+=1
        elif j>2 and extractedInformation[i+j]>='0' and extractedInformation[i+j]<='9':
          c+=1
      if i>0 and (extractedInformation[i-1]==' ' or extractedInformation[i-1]=='\n'):
        c+=1
      elif i==0:
        c+=1
      if i+10<n and extractedInformation[i+10]==' ' or extractedInformation[i+10]=='\n':
        c+=1
      elif i==n-10:
        c+=1
      if c==12:
        vote=1
        startvo=i
        break
    if vote==1:
      retval="This is a Voter ID Card with UID: " + str(extractedInformation[startvo:startvo+10])
      return retval

    pan=0
    startpan=-1
    for i in range(n-10):
      c=0
      for j in range(10):
        if j<=4 and extractedInformation[i+j]>='A' and extractedInformation[i+j]<='Z':
          c+=1
        elif j==9 and extractedInformation[i+j]>='A' and extractedInformation[i+j]<='Z':
          c+=1
        elif j>4 and j<9 and extractedInformation[i+j]>='0' and extractedInformation[i+j]<='9':
          c+=1
      if i>0 and (extractedInformation[i-1]==' ' or extractedInformation[i-1]=='\n'):
        c+=1
      elif i==0:
        c+=1
      if i+10<n and extractedInformation[i+10]==' ' or extractedInformation[i+10]=='\n':
        c+=1
      elif i==n-10:
        c+=1
      if c==12:
        pan=1
        startpan=i
        break
    if pan==1:
      #print("UID : ",extractedInformation[startpan:startpan+10])
      #print("This is a PAN card")
      retval="This is a PAN Card with UID: " + str(extractedInformation[startpan:startpan+10])
      return retval
    #else:
      #print("This is not a PAN CARD")

    #print('\n')

    aadhaar=0
    startaa=-1
    for i in range(n-14):
      c=0
      for j in range(14):
        if j==4 and extractedInformation[i+j]>=' ':
          c+=1
        elif j==9 and extractedInformation[i+j]>=' ':
          c+=1
        elif j!=4 and j!=9 and extractedInformation[i+j]>='0' and extractedInformation[i+j]<='9':
          c+=1
      if i>0 and (extractedInformation[i-1]==' ' or extractedInformation[i-1]=='\n'):
        c+=1
      elif i==0:
        c+=1
      if i+14<n and extractedInformation[i+14]==' ' or extractedInformation[i+14]=='\n':
        c+=1
      elif i==n-14:
        c+=1
      if c==16:
        aadhaar=1
        startaa=i
        break
    if aadhaar==1:
      #print("UID : ",extractedInformation[startaa:startaa+14])
      #print("This is an aadhaar card")
      retval="This is an Aadhaar Card with UID: " + str(extractedInformation[startaa:startaa+14])
      return retval
    #else:
      #print("This is not a aadhaar CARD")

    #print('\n')

    passport=0
    startpa=-1
    for i in range(n-8):
      c=0
      for j in range(8):
        if j==0 and extractedInformation[i+j]>='A' and extractedInformation[i+j]<='Z':
          c+=1
        elif j>0 and extractedInformation[i+j]>='0' and extractedInformation[i+j]<='9':
          c+=1
      if i>0 and (extractedInformation[i-1]==' ' or extractedInformation[i-1]=='\n'):
        c+=1
      elif i==0:
        c+=1
      if i+8<n and extractedInformation[i+8]==' ' or extractedInformation[i+8]=='\n':
        c+=1
      elif i==n-8:
        c+=1
      if c==10:
        passport=1
        startpa=i
        break
    if passport==1:
      #print("UID : ", extractedInformation[startpa:startpa+8])
      #print("This is a passport card")
      retval="This is a Passport Card with UID: " + str(extractedInformation[startpa:startpa+8])
      return retval
    #else:
      #print("This is not a passport card")

    #print('\n')

    licence=0
    startli=-1
    for i in range(n-16):
      c=0
      for j in range(16):
        if j<=1 and extractedInformation[i+j]>='A' and extractedInformation[i+j]<='Z':
          c+=1
        elif j==4 and extractedInformation[i+j]==' ':
          c+=1
        elif j!=4 and j>1 and extractedInformation[i+j]>='0' and extractedInformation[i+j]<='9':
          c+=1
      if i>0 and (extractedInformation[i-1]==' ' or extractedInformation[i-1]=='\n'):
        c+=1
      elif i==0:
        c+=1
      if i+16<n and extractedInformation[i+16]==' ' or extractedInformation[i+16]=='\n':
        c+=1
      elif i==n-16:
        c+=1
      if c==18:
        licence=1
        startli=i
        break
    if licence==1:
      #print("UID : ", extractedInformation[startli:startli+16])
      #print("This is a driving licence")
      retval="This is a Driving Licence Card with UID: " + str(extractedInformation[startli:startli+16])
      return retval
    #else:
      #print("This is not a driving licence")
    #print('\n')

    nrega=0
    startnr=-1
    for i in range(n-21):
      c=0
      for j in range(21):
        if j<=1 and extractedInformation[i+j]>='A' and extractedInformation[i+j]<='Z':
          c+=1
        elif j==2 and extractedInformation[i+j]=='-':
          c+=1
        elif j==5 and extractedInformation[i+j]=='-':
          c+=1
        elif j==9 and extractedInformation[i+j]=='-':
          c+=1
        elif j==13 and extractedInformation[i+j]=='-':
          c+=1
        elif j==17 and extractedInformation[i+j]=='/':
          c+=1
        elif j>2 and j!=5 and j!=9 and j!=13 and j!=17 and extractedInformation[i+j]>='0' and extractedInformation[i+j]<='9':
          c+=1
      if extractedInformation[i-1]==' ' or extractedInformation[i-1]=='\n':
        c+=1
      elif i==0:
        c+=1
      if i+21<n and extractedInformation[i+21]==' ' or extractedInformation[i+21]=='\n':
        c+=1
      elif i==n-21:
        c+=1
      if c==23:
        nrega=1
        startnr=i
        break
    if nrega==1:
      #print("UID : ", extractedInformation[startnr:startnr+21])
      #print("This is a nrega card")
      retval="This is a NREGA Card with UID: " + str(extractedInformation[startnr:startnr+21])
      return retval
    #else:
      #print("This is not a nrega card")
    retval="Please try again"
    return retval

@app.route('/',methods=['POST','GET'])
def hello_world():
    if request.method == 'POST':
        file = request.files['image'].read() ## byte file
        bg = im.open(io.BytesIO(file))
        return '<h1>{}</h1>'.format(main(bg))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=False)