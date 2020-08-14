import pytesseract
from PIL import Image
img =Image.open ('2.png')
text = pytesseract.image_to_string(img, config='')
print ("output")
print (text) 
