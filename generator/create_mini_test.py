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
# create_mini_test.py

import os
import shutil
import glob
import random
import traceback


def create_mini_test(images_dir, masks_dir, output_images_dir, output_masks_dir, sample=20):
  if os.path.exists(output_images_dir):
    shutil.rmtree(output_images_dir)
  if not os.path.exists(output_images_dir):
    os.makedirs(output_images_dir)

  if os.path.exists(output_masks_dir):
    shutil.rmtree(output_masks_dir)
  if not os.path.exists(output_masks_dir):
    os.makedirs(output_masks_dir)

  image_files = glob.glob (images_dir + "/*.jpg")
  image_files = sorted(image_files)
  image_files = random.sample(image_files, sample)

  for image_file in image_files:
    shutil.copy2(image_file, output_images_dir)
    print("Copied {}".format(image_file))

    basename = os.path.basename(image_file).split(".")[0]
    mask_file = basename + "_segmentation.png"

    mask_filepath = os.path.join(masks_dir, mask_file)
    shutil.copy2(mask_filepath, output_masks_dir)
    print("Copied {}".format(mask_filepath))



if __name__ == "__main__":
  try:
    images_dir        = "./ISIC-2017_Test_v2_Data"
    masks_dir         = "./ISIC-2017_Test_v2_Part1_GroundTruth"
    output_images_dir = "../mini_test/images/"
    output_masks_dir  = "../mini_test/masks/"
    create_mini_test(images_dir, masks_dir, output_images_dir, output_masks_dir, sample=20)

  except:
    traceback.print_exc()
