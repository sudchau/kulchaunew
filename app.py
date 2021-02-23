#WELCOME TO KULCHAU'S FLASK APP
from flask import Flask, render_template, request, redirect
from PIL import Image as im
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
  # pytesseract.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'
  img_raw=img
  #SKEW CORRECTION ON IMG
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


  #CONVERSION OF IMG AND IMG_RAW TO A FORMAT THAT CAN BE PROCESSED BY CV2
  #IMG--->IMG1
  #IMG_RAW--->IMG2
  img1 = np.array(img)
  img1 = img1[:, :, ::-1].copy()
  img1_raw = img1
  img1 = cv2.medianBlur(img1,5)

  extractedInformation1 = pytesseract.image_to_string(img1)
  #IMG1 AND IMG1_RAW ARE THE SKEW CORRECTED IMAGES


  img2 = np.array(img_raw)
  img2 = img2[:,:,::-1].copy()
  img2_raw = img2
  img2 = cv2.medianBlur(img2,5)
  extractedInformation6 = pytesseract.image_to_string(img2)
  #IMG2 AND IMG2_RAW ARE THE NON - SKEW CORRECTED IMAGES


  img3 = cv2.medianBlur(img1_raw,3)
  extractedInformation3 = pytesseract.image_to_string(img3)


  img4 = cv2.medianBlur(img2_raw,3)
  extractedInformation2 = pytesseract.image_to_string(img4)


  img5 = cv2.medianBlur(img1_raw,1) 
  extractedInformation4 = pytesseract.image_to_string(img5)


  img6 = cv2.medianBlur(img2_raw,1)
  extractedInformation5 = pytesseract.image_to_string(img6)
  #IMG1, IMG3, IMG5 ARE THE PROCESSED VERSIONS OF IMG (SKEW CORRECTED)
  #IMG2, IMG4, IMG6 ARE THE PROCESSED VERSIONS OF IMG_RAW(NON - SKEW CORRECTED)


  #CONCATENATION OF ALL THE OCR STRINGS 
  extractedInformation  = str(extractedInformation1 + " " + extractedInformation2 + " " + extractedInformation3 + " " + extractedInformation4 + " " + extractedInformation5 + " " + extractedInformation6)
  n=len(extractedInformation)


  #CODE FOR SEARCHING THE FINAL STRING FOR THE UIDs SPECIFIC TO ALL TYPES OF KYCs


  #VOTER ID CHECK
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


  #PAN CARD CHECK
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
    retval="This is a PAN Card with UID: " + str(extractedInformation[startpan:startpan+10])
    return retval


  #AADHAAR CARD CHECK
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
    retval="This is an Aadhaar Card with UID: " + str(extractedInformation[startaa:startaa+14])
    return retval


  #PASSPORT CARD CHECK  
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
    retval="This is a Passport Card with UID: " + str(extractedInformation[startpa:startpa+8])
    return retval


  #DRIVING LICENCE CHECK
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
    retval="This is a Driving Licence Card with UID: " + str(extractedInformation[startli:startli+16])
    return retval


  #JOB CARD CHECK
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
    retval="This is a NREGA Card with UID: " + str(extractedInformation[startnr:startnr+21])
    return retval


  #IF NOTHING IS FOUNG 
  retval="Please try again"
  return retval


@app.route('/',methods=['POST','GET'])
def kulchau():
    if request.method == 'POST':
        file = request.files['image'].read()
        bg = im.open(io.BytesIO(file))
        answer = main(bg)
        return redirect('/{}'.format(answer))
    return render_template('index.html')


@app.route('/<result>',methods=['POST','GET'])
def new_page(result):
    # return '<h1>{}</h1>'.format(result)
    return render_template('result.html',answer=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
