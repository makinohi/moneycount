import os

from matplotlib.backends.backend_agg import FigureCanvasAgg
import io

from keras.applications.imagenet_utils import preprocess_input
from keras.backend.tensorflow_backend import set_session
from keras.preprocessing import image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.misc import imread
import tensorflow as tf

from ssd_v2 import SSD300v2
from ssd_utils import BBoxUtility



voc_classes = ['10', '100', '5', 'Boat', 'Bottle',
            'Bus', 'Car', 'Cat', 'Chair', 'Cow', 'Diningtable',
            'Dog', 'Horse','Motorbike', 'Person', 'Pottedplant',
            'Sheep', 'Sofa', 'Train', 'Tvmonitor']
NUM_CLASSES = len(voc_classes) + 1

def initialize(weight_file_path):
    np.set_printoptions(suppress=True)

    config = tf.ConfigProto()
    config.gpu_options.per_process_gpu_memory_fraction = 0.45
    set_session(tf.Session(config=config))

    input_shape = (300, 300, 3)
    model = SSD300v2(input_shape, num_classes=NUM_CLASSES)
    model.load_weights(weight_file_path, by_name=True) 

    return model

def predict(model, img):
    inputs = []

    img = image.img_to_array(img)
    img = np.asarray(img)
    inputs.append(img.copy())
    inputs = np.asarray(inputs)
    inputs = preprocess_input(inputs)
    preds = model.predict(inputs, batch_size=1, verbose=1)
    bbox_util = BBoxUtility(NUM_CLASSES)
    results = bbox_util.detection_out(preds)

     # Parse the outputs.
    det_label = results[0][:, 0]
    det_conf = results[0][:, 1]
    det_xmin = results[0][:, 2]
    det_ymin = results[0][:, 3]
    det_xmax = results[0][:, 4]
    det_ymax = results[0][:, 5]

    top_indices = [i for i, conf in enumerate(det_conf) if conf >= 0.6]  #0.6

    top_conf = det_conf[top_indices]
    top_label_indices = det_label[top_indices].tolist()
    top_xmin = det_xmin[top_indices]
    top_ymin = det_ymin[top_indices]
    top_xmax = det_xmax[top_indices]
    top_ymax = det_ymax[top_indices]

    colors = plt.cm.hsv(np.linspace(0, 1, 21)).tolist()
    plt.imshow(img / 255.)
    currentAxis = plt.gca()

    for i in range(top_conf.shape[0]):
        xmin = int(round(top_xmin[i] * img.shape[1]))
        ymin = int(round(top_ymin[i] * img.shape[0]))
        xmax = int(round(top_xmax[i] * img.shape[1]))
        ymax = int(round(top_ymax[i] * img.shape[0]))
        score = top_conf[i]
        label = int(top_label_indices[i])
        label_name = voc_classes[label - 1]
        display_txt = '{:0.2f}, {}'.format(score, label_name)
        coords = (xmin, ymin), xmax-xmin+1, ymax-ymin+1
        color = colors[label]
        currentAxis.add_patch(plt.Rectangle(*coords, fill=False, edgecolor=color, linewidth=2))
        currentAxis.text(xmin, ymin, display_txt, bbox={'facecolor':color, 'alpha':0.5})
    
    canvas = FigureCanvasAgg(currentAxis.figure)
    buf = io.BytesIO()
    plt.savefig(buf)
    buf.seek(0)
    return buf