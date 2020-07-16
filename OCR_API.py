import os.path
import json
import sys
import pytesseract
pytesseract.pytesseract.tesseract_cmd=r"C:\Program Files\Tesseract-OCR\tesseract.exe"
import re
import csv
import dateutil.parser as dparser
from flask import Flask,jsonify
from PIL import Image
from io import BytesIO
import base64
def image_preprocess(image_path):
    with open(image_path, 'r') as f:
        data = f.read()
    img = Image.open(BytesIO(base64.b64decode(data)))
    # img = Image.open(im)
    img = img.convert('RGBA')
    pix = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pix[x, y][0] < 102 or pix[x, y][1] < 102 or pix[x, y][2] < 102:
                pix[x, y] = (0, 0, 0, 255)
            else:
                pix[x, y] = (255, 255, 255, 255)
    img.save('temp.png')

def image_to_text(image_path):
    img=Image.open(image_path)
    text=pytesseract.image_to_string(img)
    return text

name = None
gender = None
ayear = None
uid = None
yearline = []
genline = []
nameline = []
text1 = []
text2 = []
uid = set()
genderStr = '(Female|Male|emale|male|ale|FEMALE|MALE|EMALE)$'

def year_of_birth(text):
# Searching for Year of Birth
    lines = text
    global text1
    global text2
    global yearline
    global ayear
# print (lines)
    for wordlist in lines.split('\n'):
        xx = wordlist.split()
        if [w for w in xx if re.search('(Year|Birth|irth|YoB|YOB:|DOB:|DOB)$', w)]:
            yearline = wordlist
            break
        else:
            text1.append(wordlist)
    try:
        text2 = text.split(yearline, 1)[1]
    except Exception:
        pass

    try:
        yearline = re.split('Year|Birth|irth|YoB|YOB:|DOB:|DOB', yearline)[1:]
        yearline = ''.join(str(e) for e in yearline)
    #     if yearline:
    #         ayear = dparser.parse(yearline, fuzzy=True).year
    except Exception:
        pass

def E_gender(text):
    global genline
    global gender
    global text2
    lines=text
# # Searching for Gender
    try:
        for wordlist in lines.split('\n'):
            xx = wordlist.split()
            if [w for w in xx if re.search(genderStr, w)]:
                genline = wordlist
                break

        if 'Female' in genline or 'FEMALE' in genline:
            gender = "Female"
        if 'Male' in genline or 'MALE' in genline:
            gender = "Male"

        text2 = text.split(genline, 1)[1]
    except Exception:
        pass

def E_uid():
# Searching for UID
    global uid
    # global text2
    try:
        newlist = []
        for xx in text2.split('\n'):
            newlist.append(xx)
        newlist = list(filter(lambda x: len(x) > 12, newlist))
        for no in newlist:
            print(no)
            if re.match("^[0-9 ]+$", no):
                uid.add(no)
    except Exception:
        pass

#####################################
path='aadhar.txt'
image_preprocess(path) ###this will save temp.png
#####################################
text=image_to_text('temp.png')
# print(text)
##################################
year_of_birth(text)
E_gender(text)
E_uid()
# print(ayear)
# print(gender)
# print(uid)
#######################################################
data = {}
data['Name'] = name
data['Gender'] = gender
data['Birth Date'] = yearline
# if len(list(uid)) > 1:
data['Uid'] = list(uid)[0]
# else:
#     data['Uid'] = None
####################################API###############
app=Flask(__name__)
@app.route('/')
def image_to_json():
    return jsonify(data)

if __name__=="__main__":
    app.run()