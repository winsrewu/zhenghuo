from PIL import Image
from numpy import asarray
import json
 
img = Image.open('1.png')
im_gray = img.convert('L')

points = []

for y in range(img.height):
    for x in range(img.width):
            if x % 2 != 0 or y % 2 != 0:
                  continue
            if im_gray.getpixel((x, y)) < 220:
                  points.append({"x": x / img.width, "y": y / img.height})

res = json.dumps(points)
print(res)

with open('output.txt', 'w') as f:
      f.write(res)