#!usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot 
from matplotlib import pyplot as plt
import os
import tensorflow as tf
from PIL import Image
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

import datetime
# 关闭tensorflow警告
import time
import argparse
import sys
reload(sys)
sys.setdefaultencoding('utf8')

os.environ['TF_CPP_MIN_LOG_LEVEL']='3'

detection_graph = tf.Graph()

# 加载模型数据-------------------------------------------------------------------------------------------------------
def loading(model_name):

    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        PATH_TO_CKPT = '/home/yanjieliu/models/models/research/object_detection/pretrained_models/'+model_name + '/frozen_inference_graph.pb'
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
    return detection_graph



# Detection检测-------------------------------------------------------------------------------------------------------
def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)
# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('/home/yanjieliu/models/models/research/object_detection/data', 'mscoco_label_map.pbtxt')
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=90, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

def Detection(args):
    image_path=args.image_path
    loading(args.model_name)
    #start = time.time()
    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:
            # for image_path in TEST_IMAGE_PATHS:
            image = Image.open(image_path)

            # the array based representation of the image will be used later in order to prepare the
            # result image with boxes and labels on it.
            image_np = load_image_into_numpy_array(image)

            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image_np, axis=0)
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

            # Each box represents a part of the image where a particular object was detected.
            boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

            # Each score represent how level of confidence for each of the objects.
            # Score is shown on the result image, together with the class label.
            scores = detection_graph.get_tensor_by_name('detection_scores:0')
            classes = detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name('num_detections:0')

            # Actual detection.
            (boxes, scores, classes, num_detections) = sess.run(
                [boxes, scores, classes, num_detections],
                feed_dict={image_tensor: image_np_expanded})

            # Visualization of the results of a detection.将识别结果标记在图片上
            vis_util.visualize_boxes_and_labels_on_image_array(
                 image_np,
                 np.squeeze(boxes),
                 np.squeeze(classes).astype(np.int32),
                 np.squeeze(scores),
                 category_index,
                 use_normalized_coordinates=True,
                 line_thickness=8)
            # output result输出
            for i in range(3):
                if classes[0][i] in category_index.keys():
                    class_name = category_index[classes[0][i]]['name']
                else:
                    class_name = 'N/A'
                print("object：%s gailv：%s" % (class_name, scores[0][i]))
                
            # matplotlib输出图片
            # Size, in inches, of the output images.
            IMAGE_SIZE = (20, 12)
            plt.figure(figsize=IMAGE_SIZE)
            plt.imshow(image_np)
            plt.show()

def parse_args():
    '''parse args'''
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_path', default='/home/yanjieliu/dataset/img_test/p4.jpg')
    parser.add_argument('--model_name',
                        default='mask_rcnn_inception_resnet_v2_atrous_coco_2018_01_28')
    return parser.parse_args()


# 运行
start = time.time()
Detection(parse_args())
end = time.time()
print('time:\n')
print str(end-start)

with open('./outputs/1to10test_outputs.txt', 'a') as f:
    f.write('\n')
    f.write(str(end-start))