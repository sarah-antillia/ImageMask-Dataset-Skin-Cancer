# Copyright 2023 antillia.com Toshiyuki Arai
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# 2023/08/04 to-arai antillia.com
# 2023/08/11 Modified augment method to shrink an image and a mask.
# 2023/08/17 Modified augment method to mix rotation and shrinking operation to image and mask.
# 2024/03/17 Modified augment parametger = False.
# 2024/03/17 Modified resize=512.

import os
import shutil

import glob
import cv2
import numpy as np
import traceback
from PIL import Image, ImageOps, ImageFilter


class ImageMaskDatasetGenerator:
  def __init__(self, resize=512): # 256
    
    self.RESIZE = resize


  def augment(self, image, output_dir, filename, mask=False):
    # 2023/08/02
    #ANGLES = [30, 90, 120, 150, 180, 210, 240, 270, 300, 330]
    ANGLES = [0, 90, 180, 270]
    #ANGLES = [90, 270]

    for angle in ANGLES:
      rotated_image = image.rotate(angle)
      output_filename = "rotated_" + str(angle) + "_" + filename
      rotated_image_file = os.path.join(output_dir, output_filename)
      #cropped  =  self.crop_image(rotated_image)
      SHRINKS = [0.7, 1.0]
      #SHRINKS = [0.8]
      w, h = rotated_image.size
      for shrink in SHRINKS:
        rw = int (w * shrink)
        rh = int (h * shrink)
     
        resized = rotated_image.resize((rw, rh))
        squared = self.paste(resized, mask)
        ratio   = str(shrink).replace(".", "_")
        output_filename = "rotated_" + str(angle) + "_"  + "shrinked_" + ratio + "_" + filename
        image_filepath  = os.path.join(output_dir, output_filename)
        squared.save(image_filepath)
        print("=== Saved {}".format(image_filepath))

    # Create mirrored image
    """
    mirrored = ImageOps.mirror(image)
    output_filename = "mirrored_" + filename
    image_filepath = os.path.join(output_dir, output_filename)
    #cropped = self.crop_image(mirrored)
    
    mirrored.save(image_filepath)
    print("=== Saved {}".format(image_filepath))
  
    # Create flipped image
    flipped = ImageOps.flip(image)
    output_filename = "flipped_" + filename

    image_filepath = os.path.join(output_dir, output_filename)
    #cropped = self.crop_image(flipped)

    flipped.save(image_filepath)
    print("=== Saved {}".format(image_filepath))
    """

  def generate(self, input_images_dir, input_masks_dir, images_output_dir, masks_output_dir,
                 augment=True):
    if os.path.exists(images_output_dir):
      shutil.rmtree(images_output_dir)

    if not os.path.exists(images_output_dir):
      os.makedirs(images_output_dir)

    if os.path.exists(masks_output_dir):
      shutil.rmtree(masks_output_dir)

    if not os.path.exists(masks_output_dir):
      os.makedirs(masks_output_dir)

    image_files = glob.glob(input_images_dir + "/*.jpg")
    
    mask_files  = glob.glob(input_masks_dir + "/*.png")
    num_images  = len(image_files)
    num_masks   = len(mask_files)
    
    print("=== generate num_image_files {} num_masks_files {}".format(num_images, num_masks))

    if num_images != num_masks:
      raise Exception("Not matched image_files and mask_files")
    
    
    for image_file in image_files:
      try:
        basename = os.path.basename(image_file)
        name     = basename.split(".")[0]
        mask_filepath  = os.path.join(input_masks_dir, name + "_segmentation.png")

        image = Image.open(image_file).convert("RGB")
        image = self.resize_to_square(image)
        if augment:
          self.augment(image, images_output_dir, basename, mask=False)
        else:
          image_filepath = os.path.join(images_output_dir,  basename)
          image.save(image_filepath)
          print("=== Saved {}".format(image_filepath))
        mask = Image.open(mask_filepath).convert("RGB")
        #mask = self.create_mono_color_mask(mask)
        mask = self.resize_to_square(mask)
        if augment:
          self.augment(mask, masks_output_dir,  basename, mask=True)
        else:
          mask_filepath = os.path.join(masks_output_dir,  basename)
          mask.save(mask_filepath)
          print("=== Saved {}".format(mask_filepath))
      except:
        traceback.print_exc()

  def resize_to_square(self, image):
     w, h  = image.size

     bigger = w
     if h > bigger:
       bigger = h
     pixel = image.getpixel((w-80, h-80))
     background = Image.new("RGB", (bigger, bigger), pixel)
    
     x = (bigger - w) // 2
     y = (bigger - h) // 2
     background.paste(image, (x, y))
     background = background.resize((self.RESIZE, self.RESIZE))

     return background
  
  def paste(self, image, mask):
     w, h = image.size
  
     pixel = image.getpixel((w-80, h-80))
     if mask:
       pixel = (0, 0, 0)
    
     background = Image.new("RGB", (self.RESIZE, self.RESIZE), pixel)
     x = (self.RESIZE - w)//2
     y = (self.RESIZE - h)//2

     background.paste(image, (x, y))
     return background


  def create_mono_color_mask(self, mask, mask_color=(255, 255, 255)):
    rw, rh = mask.size    
    xmask = Image.new("RGB", (rw, rh))
    #print("---w {} h {}".format(rw, rh))

    for i in range(rw):
      for j in range(rh):
        color = mask.getpixel((i, j))
        (r, g, b) = color
        # If color is blue
        if r>4 or g >4 or b > 4:
          xmask.putpixel((i, j), mask_color)

    return xmask
  
  
if __name__ == "__main__":
  try:
   generator = ImageMaskDatasetGenerator()

   input_images_dir  = "./ISIC-2017_Training_Data/"
   input_masks_dir   = "./ISIC-2017_Training_Part1_GroundTruth/"

   images_output_dir = "../Skin-Cancer-ImageMask-Dataset/train/images/"
   masks_output_dir  = "../Skin-Cancer-ImageMask-Dataset/train/masks/"

   generator.generate(input_images_dir, input_masks_dir, 
   					  images_output_dir, masks_output_dir, augment=False)
   

   input_images_dir  = "./ISIC-2017_Validation_Data/"
   input_masks_dir   = "./ISIC-2017_Validation_Part1_GroundTruth/"

   images_output_dir = "../Skin-Cancer-ImageMask-Dataset/valid/images/"
   masks_output_dir  = "../Skin-Cancer-ImageMask-Dataset/valid/masks/"
   generator.generate(input_images_dir, input_masks_dir, 
   					  images_output_dir, masks_output_dir, augment=False)

   input_images_dir  = "./ISIC-2017_Test_v2_Data/"
   input_masks_dir   = "./ISIC-2017_Test_v2_Part1_GroundTruth/"

   images_output_dir = "../Skin-Cancer-ImageMask-Dataset/test/images/"
   masks_output_dir  = "../Skin-Cancer-ImageMask-Dataset/test/masks/"
   generator.generate(input_images_dir, input_masks_dir, 
   					  images_output_dir, masks_output_dir, augment=False)

  except:
    traceback.print_exc()
