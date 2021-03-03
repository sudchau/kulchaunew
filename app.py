#WELCOME TO KULCHAU'S FLASK APP --->


#LIBRARIES
from flask import Flask, render_template, request, redirect
from PIL import Image as im
import pytesseract
import io
import cv2
import numpy as np
from scipy.ndimage import interpolation as inter
import requests


app = Flask(__name__)


#SKEW CORRECTION FUNCTION --->
def correct_skew(image, delta=1, limit=5):
  def determine_score(arr, angle):
    data = inter.rotate(arr, angle, reshape=False, order=0)
    histogram = np.sum(data, axis=1)
    score = np.sum((histogram[1:] - histogram[:-1]) ** 2)
    return histogram, score

  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1] 

  scores = []
  angles = np.arange(-limit, limit + delta, delta)

  for angle in angles:
    histogram, score = determine_score(thresh, angle)
    scores.append(score)

  best_angle = angles[scores.index(max(scores))]

  (h, w) = image.shape[:2]
  center = (w // 2, h // 2)
  M = cv2.getRotationMatrix2D(center, best_angle, 1.0)
  rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, \
              borderMode=cv2.BORDER_REPLICATE)

  return best_angle, rotated


#DOUBLE CHECK FUNCTION = RESPONSIBLE FOR FINDIND HEURISTIC CLOSENESS INDEX --->


#DOUBLE CHECK FUNCTION FOR AADHAAR CARD --->
def aadhaar_double_check(extractedInformation):
  n = len(extractedInformation)
  to_check1 = "DOB : **/##/^^^^ "
  to_check2 = "Year of Birth : ^^^^ "
  max_score = len(to_check1) * len(to_check2)
  max_match1 = 0
  max_match2 = 0

  for i in range(n - len(to_check2)):
    curr_match2 = 0
    yyyy = "0"
    for j in range(len(to_check2)):
      c = extractedInformation[i + j];
      if to_check2[j] == '^' and c >= '0' and c <= '9':
        yyyy = yyyy + c
      elif to_check2[j] == c:
        curr_match2 += 1
    if int(yyyy) <= 2021 and int(yyyy) >= 1800:
      curr_match2 += 4
    max_match2 = max(max_match2, curr_match2)

  for i in range(n - len(to_check1)):
    curr_match1 = 0
    dd = "0"
    mm = "0" 
    yyyy = "0"
    for j in range(len(to_check1)):
      c = extractedInformation[i + j];
      if to_check1[j] == '*' and c >= '0' and c <= '9':
        dd = dd + c
      elif to_check1[j] == '#' and c >= '0' and c <= '9':
        mm = mm + c
      elif to_check1[j] == '^' and c >= '0' and c <= '9':
        yyyy = yyyy + c
      elif to_check1[j] == c:
        curr_match1 += 1
    if int(dd) <= 31 and int(dd) >= 1:
      curr_match1 += 2
    if int(mm) <= 12 and int(mm) >= 1:
      curr_match1 += 2
    if int(yyyy) <= 2021 and int(yyyy) >= 1800:
      curr_match1 += 4
    max_match1 = max(max_match1, curr_match1)

  max_match1 = max_match1 * len(to_check2)
  max_match2 = max_match2 * len(to_check1)
  final_score = max(max_match1, max_match2) * 100 / max_score
  return str(final_score)


#DOUBLE CHECK FUNCTION FOR PASSPORT 
def passport_double_check(extractedInformation):
  n = len(extractedInformation)
  to_check1 = "REPUBLIC OF INDIA"
  to_check2 = "Place of Issue"
  max_score = len(to_check1) * len(to_check2)
  max_match1 = 0
  max_match2 = 0

  for i in range(n - len(to_check1)):
    curr_match1 = 0
    for j in range(len(to_check1)):
      if to_check1[j] == extractedInformation[i + j]:
        curr_match1 += 1
    max_match1 = max(max_match1, curr_match1)

  for i in range(n - len(to_check2)):
    curr_match2 = 0
    for j in range(len(to_check2)):
      if to_check2[j] == extractedInformation[i + j]:
        curr_match2 += 1
    max_match2 = max(max_match2, curr_match2)

  max_match1 = max_match1 * len(to_check2)
  max_match2 = max_match2 * len(to_check1)
  final_score = max(max_match1, max_match2) * 100 / max_score
  return str(final_score)


#DOUBLE CHECK FUNCTION FOR DRIVING LICENCE --->
def licence_double_check(extractedInformation):
  n = len(extractedInformation)
  to_check1 = "AUTHORISATION TO DRIVE FOLLOWING CLASS"
  to_check2 = "DOB : **-##-^^^^ "
  max_score = len(to_check1) * len(to_check2)
  max_match1 = 0
  max_match2 = 0

  for i in range(n - len(to_check1)):
    curr_match1 = 0
    for j in range(len(to_check1)):
      c = extractedInformation[i + j];
      if to_check1[j] == c:
        curr_match1 += 1
    max_match1 = max(max_match1, curr_match1)

  for i in range(n - len(to_check2)):
    curr_match2 = 0
    dd = "0"
    mm = "0" 
    yyyy = "0"
    for j in range(len(to_check2)):
      c = extractedInformation[i + j];
      if to_check2[j] == '*' and c >= '0' and c <= '9':
        dd = dd + c
      elif to_check2[j] == '#' and c >= '0' and c <= '9':
        mm = mm + c
      elif to_check2[j] == '^' and c >= '0' and c <= '9':
        yyyy = yyyy + c
      elif to_check2[j] == c:
        curr_match2 += 1
    if int(dd) <= 31 and int(dd) >= 1:
      curr_match2 += 2
    if int(mm) <= 12 and int(mm) >= 1:
      curr_match2 += 2
    if int(yyyy) <= 2021 and int(yyyy) >= 1800:
      curr_match2 += 4
    max_match2 = max(max_match2, curr_match2)

  max_match1 = max_match1 * len(to_check2)
  max_match2 = max_match2 * len(to_check1)
  final_score = max(max_match1, max_match2) * 100 / max_score
  return str(final_score)


#DOUBLE CHECK FUNCTION FOR PAN CARD
def pan_double_check(extractedInformation):
  n = len(extractedInformation)
  to_check1 = "income tax department"
  to_check2 = "permanent account number"
  max_score = len(to_check1) * len(to_check2)
  max_match1 = 0
  max_match2 = 0

  for i in range(n - len(to_check1)):
    curr_match1 = 0
    for j in range(len(to_check1)):
      c = extractedInformation[i + j]
      if c >= 'A' and c <= 'Z':
        c = c.lower()
      if to_check1[j] == c:
        curr_match1 += 1
    max_match1 = max(max_match1, curr_match1)

  for i in range(n - len(to_check2)):
    curr_match2 = 0
    for j in range(len(to_check2)):
      c = extractedInformation[i + j]
      if c >= 'A' and c <= 'Z':
        c = c.lower()
      if to_check2[j] == c:
        curr_match2 += 1
    max_match2 = max(max_match2, curr_match2)

  max_match1 = max_match1 * len(to_check2)
  max_match2 = max_match2 * len(to_check1)
  final_score = max(max_match1, max_match2) * 100 / max_score
  return str(final_score)


#DOUBLE CHECK FOR VOTER ID
def voter_double_check(extractedInformation):
  n = len(extractedInformation)
  to_check1 = "election commission of india"
  to_check2 = "date of birth"
  max_score = len(to_check1) * len(to_check2)
  max_match1 = 0
  max_match2 = 0

  for i in range(n - len(to_check1)):
    curr_match1 = 0
    for j in range(len(to_check1)):
      c = extractedInformation[i + j];
      if c >= 'A' and c <= 'Z':
        c = c.lower()
      if to_check1[j] == c:
        curr_match1 += 1
    max_match1 = max(max_match1, curr_match1)

  for i in range(n - len(to_check2)):
    curr_match2 = 0
    for j in range(len(to_check2)):
      c = extractedInformation[i + j];
      if c >= 'A' and c <= 'Z':
        c = c.lower()
      if to_check2[j] == c:
        curr_match2 += 1
    max_match2 = max(max_match2, curr_match2)
    
  max_match1 = max_match1 * len(to_check2)
  max_match2 = max_match2 * len(to_check1)
  final_score = max(max_match1, max_match2) * 100 / max_score
  return str(final_score)


#CODE FOR OUR ALGORITHM --->
def OUR_ALGORITHM(extractedInformation):
  n=len(extractedInformation)
  #CODE FOR SEARCHING THE FINAL STRING FOR THE UIDs SPECIFIC TO ALL TYPES OF KYCs


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
    uid=str(extractedInformation[startaa:startaa+14])
    kyc_type="Aadhaar Card"
    final_score=aadhaar_double_check(extractedInformation)
    print(final_score)
    return uid, kyc_type,final_score
 

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
    uid=str(extractedInformation[startpan:startpan+10])
    kyc_type="PAN Card"
    final_score=pan_double_check(extractedInformation)
    return uid, kyc_type, final_score


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
    uid=str(extractedInformation[startli:startli+16])
    kyc_type="Driving Licence"
    final_score=licence_double_check(extractedInformation)
    return uid, kyc_type,final_score


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
    uid=str(extractedInformation[startpa:startpa+8])
    kyc_type="Passport"
    final_score=passport_double_check(extractedInformation)
    return uid, kyc_type,final_score


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
    uid=str(extractedInformation[startvo:startvo+10])
    kyc_type="Voter's Identity Card"
    final_score=voter_double_check(extractedInformation)
    return uid, kyc_type,final_score


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
    uid=str(extractedInformation[startnr:startnr+21])
    kyc_type="NREGA Card"
    final_score=aadhaar_double_check(extractedInformation)
    return uid, kyc_type,final_score


  #IF NOTHING IS FOUND
  uid="Please try again, the image was not clear enough"
  kyc_type= "none found"
  return uid, kyc_type, "---"


#MAIN WEBSITE FUNCTION -->
def main(img):
  img.thumbnail(size=(1500,1500))
  img_raw = img
  #CONVERSION OF IMG AND IMG_RAW TO A FORMAT THAT CAN BE PROCESSED BY CV2
  #IMG--->IMG1
  #IMG_RAW--->IMG2
  img1 = np.array(img)
  img1 = img1[:, :, ::-1].copy()


  #SKEW CORRECTION ON IMG
  angle, img1 = correct_skew(img1)
  img1_raw = img1


  img1 = cv2.medianBlur(img1_raw,5)
  extractedInformation1 = pytesseract.image_to_string(img1)
  #IMG1 AND IMG1_RAW ARE THE SKEW CORRECTED IMAGES


  img2 = np.array(img_raw)
  img2 = img2[:,:,::-1].copy()
  img2_raw = img2


  img2 = cv2.medianBlur(img2_raw,5)
  extractedInformation2 = pytesseract.image_to_string(img2)
  #IMG2 AND IMG2_RAW ARE THE NON - SKEW CORRECTED IMAGES


  img3 = cv2.medianBlur(img1_raw,3)
  extractedInformation3 = pytesseract.image_to_string(img3)


  img4 = cv2.medianBlur(img2_raw,3)
  extractedInformation4 = pytesseract.image_to_string(img4)


  img5 = cv2.medianBlur(img1_raw,1) 
  extractedInformation5 = pytesseract.image_to_string(img5)


  img6 = cv2.medianBlur(img2_raw,1)
  extractedInformation6 = pytesseract.image_to_string(img6)
  #IMG1, IMG3, IMG5 ARE THE PROCESSED VERSIONS OF IMG (SKEW CORRECTED)
  #IMG2, IMG4, IMG6 ARE THE PROCESSED VERSIONS OF IMG_RAW(NON - SKEW CORRECTED)


  #CONCATENATION OF ALL THE OCR STRINGS 
  extractedInformation  = "   " + str(extractedInformation1 + " " + extractedInformation2 + " " + extractedInformation3 + " " + extractedInformation4 + " " + extractedInformation5 + " " + extractedInformation6) + "   "
  print(extractedInformation)

  return OUR_ALGORITHM(extractedInformation)


#MAIN FUNCTIONS FOR MOBILE APPLICATION (FOR FASTER EXECUTION ON APP)---> 
def main1(img):
  #img.thumbnail(size=(1000,1000))
  img1 = np.array(img)
  img1 = img1[:, :, ::-1].copy()
  img1 = cv2.medianBlur(img1,5)
  extractedInformation1 = pytesseract.image_to_string(img1)
  extractedInformation = "  " + extractedInformation1 + "  "
  return OUR_ALGORITHM(extractedInformation)
  

def main2(img):
  #img.thumbnail(size=(1000,1000))
  img2 = np.array(img)
  img2 = img2[:, :, ::-1].copy()
  img2 = cv2.medianBlur(img2,3)
  extractedInformation1 = pytesseract.image_to_string(img2)
  extractedInformation = "  " + extractedInformation1 + "  "
  return OUR_ALGORITHM(extractedInformation)


def main3(img):
  #img.thumbnail(size=(1000,1000))
  img3 = np.array(img)
  img3 = img3[:, :, ::-1].copy()
  img3 = cv2.medianBlur(img3,1)
  extractedInformation1 = pytesseract.image_to_string(img3)
  extractedInformation = "  " + extractedInformation1 + "  "
  return OUR_ALGORITHM(extractedInformation)


#SERVERS --->

@app.route('/',methods = ['POST', 'GET'])
def kulchau():
  if request.method == 'POST':
    file = request.files['image'].read()
    bg = im.open(io.BytesIO(file))
    uid, kyc_type,final_score = main(bg)
    return redirect('/result/{}-{}-{}'.format(uid, kyc_type, final_score))
  return render_template('index.html')
 

@app.route('/server',methods=['POST','GET'])
def forserver():
  url = request.form['image']
  response = requests.get(url)
  flag = request.form['flag']
  bg = im.open(io.BytesIO(response.content))
  #uid, kyc_type,final_score = main(bg)
  #return "This is a {}, with UID = {}\nWith Heuristic Closeness Percentage = {}%".format(kyc_type,uid,final_score)
  #a, b = bg.size
  #print("{} and {}".format(a,b))
  if flag=='0':
    newflag = 1    
    uid, kyc_type,final_score = main1(bg)
    if(kyc_type=='none found'):
      newflag = 0
    return "{}This is a {}, with UID = {}\nWith Heuristic Closeness Index = {}%".format(newflag,kyc_type,uid,final_score)
  if flag=='1':
    newflag = 1    
    uid, kyc_type,final_score = main2(bg)
    if(kyc_type=='none found'):
      newflag = 0
    return "{}This is a {}, with UID = {}\nWith Heuristic Closeness Index = {}%".format(newflag,kyc_type,uid,final_score)
  if flag=='2':
    newflag = 1    
    uid, kyc_type,final_score = main3(bg)
    if(kyc_type=='none found'):
      newflag = 0
    return "{}This is a {}, with UID = {}\nWith Heuristic Closeness Index = {}%".format(newflag,kyc_type,uid,final_score)


@app.route('/result/<result>',methods=['POST', 'GET'])
def new_page(result):
  uid = ""
  kyc_type = ""
  final_score = ""
  j = -1
  for i in range(len(result)):
    if(result[i] == '-'):
      j = i
      break
    else:
      uid = uid + result[i]
  for i in range(j + 1, len(result)):
    if(result[i] == '-'):
      j = i
      break
    else:
      kyc_type = kyc_type + result[i]

  for i in range(j + 1, len(result)):
    final_score = final_score + result[i]

  flag=True
  if kyc_type == 'none found':
    flag = False
  return render_template('result.html', identif = kyc_type, uiid = uid, flag = flag, final_score = final_score)

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug = True)

