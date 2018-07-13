import sys
import io
import base64
import tensorflow as tf
from PIL import Image
import numpy as np
from flask import Flask, jsonify, render_template, request, redirect, url_for, render_template, flash, json, send_file
sys.path.append('./deep_learning')
from deep_learning import dl

app = Flask(__name__)
graph = tf.get_default_graph()
model = dl.initialize('./deep_learning/weight/money_weights.hdf5')

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/api/moneycount', methods=['POST'])
def count_money():
    global graph
    with graph.as_default():
        img_decoded = base64.b64decode(request.json)
        img_binarystream = io.BytesIO(img_decoded)
        img_pil = Image.open(img_binarystream)
        img = dl.predict(model, img_pil)

        return send_file(img, mimetype='image/png')

if __name__ == '__main__':
    app.run()