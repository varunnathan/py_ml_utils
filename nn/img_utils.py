import os, math
import numpy as np
from PIL import Image, ImageChops

def load_imgs(path, files=None, grayscale=False):
  if files is None: 
    def isimg(f):
      ext = f.split('.')[-1]
      return ext in ['jpg', 'gif', 'png', 'bmp']      
    files = [f for f in os.listdir(path) if isimg(f)]
  files = [os.path.join(path, f) for f in files]
  return [Image.open(f).convert("L" if grayscale else "RGB") for f in files]

def save_imgs(filename, imgs, size=800):
  if '.' not in filename: filename += '.png'
  new_im = Image.new('RGB', (size, size))  
  rows = cols = math.ceil(math.sqrt(len(imgs)))
  if (rows - 1) * cols >= len(imgs): rows -= 1
  size_s = int(math.ceil(size / float(cols))) 
  idx = 0 
  for y in xrange(0, size, size_s):
    for x in xrange(0, size, size_s):
      if idx == len(imgs): continue      
      im = Image.fromarray(imgs[idx])
      w_border = Image.new("RGB", (size_s, size_s), (255, 255, 255))
      im = im.resize((size_s - 2, size_s - 2))
      w_border.paste(im, (1, 1))      
      idx += 1      
      new_im.paste(w_border, (x, y))
  new_im.save(filename)

def save_img(filename, img):
  if '.' not in filename: filename += '.png'
  if type(img) is np.array: img = Image.fromarray(img)
  img.save(filename)

def resize_imgs(imgs, size):
  return [resize_img(i, size) for i in imgs]

def resize_img(img, size):
  img = img.copy()
  img.thumbnail(size, Image.ANTIALIAS)
  new_size = img.size
  img = img.crop( (0, 0, size[0], size[1]))

  offset_x = max( (size[0] - new_size[0]) / 2, 0 )
  offset_y = max( (size[1] - new_size[1]) / 2, 0 )

  return ImageChops.offset(img, offset_x, offset_y)  

def rotate_imgs(imgs, angle=20): return [rotate_img(i, angle) for i in imgs]

def rotate_img(img, angle=20): return img.rotate(_get_rng_from_min_max(angle))

def toarr_imgs(imgs, keras_style=True):
  arr = np.array([np.asarray(img) for img in imgs])
  if keras_style: arr = np.swapaxes(arr,3,1)
  return arr

def flip_imgs(imgs, horizontal=True):
  return [flip_img(img, horizontal) for img in imgs]

def flip_img(img, horizontal=True):
  return img.transpose(Image.FLIP_LEFT_RIGHT if horizontal else Image.FLIP_TOP_BOTTOM)

def zoom_imgs(imgs, factor=10):
  return np.array([zoom_img(i, factor) for i in imgs])

def zoom_img(img, factor=10):
  rows, cols = img.shape[:2]  
  if isinstance(factor, (list, tuple)): factor = np.random.uniform(factor[0], factor[1])
  else: factor = np.random.uniform(factor/2., factor)
  pts1 = np.float32([[factor,factor],[cols-factor,factor],[factor,rows-factor],[cols-factor, rows-factor]])
  pts2 = np.float32([[0,0],[cols,0],[0,rows],[cols,rows]])
  M = cv2.getPerspectiveTransform(pts1, pts2)
  return cv2.warpPerspective(img,M,(rows,cols))

def save_history_loss(filename, history):
  if '.' not in filename: filename += '.png'

  losses = {'loss': history['loss']}
  if 'val_loss' in history: losses.add('val_loss', history['val_loss'])
  
  save_losses(filename, losses)
  
def save_losses(filename, losses):
  if '.' not in filename: filename += '.png'

  x = history['epoch']
  legend = losses.keys

  for v in losses.values: plt.plot(np.arange(len(v)) + 1, v, marker='.')

  plt.title('Loss over epochs')
  plt.xlabel('Epochs')
  plt.xticks(history['epoch'], history['epoch'])
  plt.legend(legend, loc = 'upper right')
  plt.savefig(filename)

def _get_rng_from_min_max(num):
  if isinstance(num, (list, tuple)): return np.random.uniform(num[0], num[1])
  else: return np.random.uniform(-num, num)