
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import sys
sys.path.append("../eva/")

import tensorflow as tf
from scipy import misc
import cv2
import matplotlib.pyplot as plt
import numpy as np
import argparse
import facenet
import detect_face
import os
from os.path import join as pjoin
import sys
import time
import math
import pickle
from sklearn.svm import SVC
from sklearn.externals import joblib
from datetime import datetime
from bot import Bot
from pydub import AudioSegment
from pydub.playback import play
import requests
import json
from threading import Timer

num_frames = 8
confidence_thrushhold = 0.7


class Head(object):

    def __init__(self, current_user):
        self.bot = Bot(current_user)
        self.checked = False
        self.t = None

    def start(self):
        dubug_mode = False

        dubug_mode = True    # _____________testing

        with tf.Graph().as_default():
            gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.6)
            sess = tf.Session(config=tf.ConfigProto(
                gpu_options=gpu_options, log_device_placement=False))
            with sess.as_default():

                pnet, rnet, onet = detect_face.create_mtcnn(sess, '')

                minsize = 20  # minimum size of face
                threshold = [0.6, 0.7, 0.7]  # three steps's threshold
                factor = 0.709  # scale factor
                margin = 44
                frame_interval = 3
                batch_size = 1000
                image_size = 182
                input_image_size = 160

                HumanNames = []

                with open("names") as f:
                    for line in f:
                        HumanNames.append(line.strip())

                HumanNames.sort()  # train human name

                modeldir = 'model.pb'
                facenet.load_model(modeldir)

                images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
                embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
                phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
                embedding_size = embeddings.get_shape()[1]

                classifier_filename = 'classifier/my_classifier.pkl'
                classifier_filename_exp = os.path.expanduser(
                    classifier_filename)
                with open(classifier_filename_exp, 'rb') as infile:
                    (model, class_names) = pickle.load(infile)

                # capture
                video_capture = cv2.VideoCapture(0)
                c = 0

                pred_list = []

                self.face_recog_prompt()

                while True:
                    self.checks()

                    if self.bot.check_user_logedin():  # EVA / BOT
                        self.bot.run()

                    else:
                        # do face recognition

                        ret, frame = video_capture.read()

                        # resize frame (optional)
                        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

                        timeF = frame_interval

                        if (c % timeF == 0):
                            find_results = []

                            if frame.ndim == 2:
                                frame = facenet.to_rgb(frame)
                            frame = frame[:, :, 0:3]
                            bounding_boxes, _ = detect_face.detect_face(
                                frame, minsize, pnet, rnet, onet, threshold, factor)
                            nrof_faces = bounding_boxes.shape[0]

                            if nrof_faces > 0:
                                det = bounding_boxes[:, 0:4]
                                img_size = np.asarray(frame.shape)[0:2]

                                cropped = []
                                scaled = []
                                scaled_reshape = []
                                bb = np.zeros((nrof_faces, 4), dtype=np.int32)

                                for i in range(nrof_faces):
                                    emb_array = np.zeros((1, embedding_size))

                                    bb[i][0] = det[i][0]
                                    bb[i][1] = det[i][1]
                                    bb[i][2] = det[i][2]
                                    bb[i][3] = det[i][3]

                                    # inner exception
                                    if bb[i][0] <= 0 or bb[i][1] <= 0 or bb[i][2] >= len(frame[0]) or bb[i][3] >= len(frame):
                                        continue

                                    cropped.append(
                                        frame[bb[i][1]:bb[i][3], bb[i][0]:bb[i][2], :])
                                    cropped[0] = facenet.flip(
                                        cropped[0], False)
                                    scaled.append(misc.imresize(
                                        cropped[0], (image_size, image_size), interp='bilinear'))
                                    scaled[0] = cv2.resize(scaled[0], (input_image_size, input_image_size),
                                                           interpolation=cv2.INTER_CUBIC)
                                    scaled[0] = facenet.prewhiten(scaled[0])
                                    scaled_reshape.append(
                                        scaled[0].reshape(-1, input_image_size, input_image_size, 3))
                                    feed_dict = {
                                        images_placeholder: scaled_reshape[0], phase_train_placeholder: False}

                                    emb_array[0, :] = sess.run(
                                        embeddings, feed_dict=feed_dict)

                                    predictions = model.predict_proba(
                                        emb_array)
                                    best_class_indices = np.argmax(
                                        predictions, axis=1)

                                    pred_list.append(predictions)

                                    if num_frames == len(pred_list):
                                        avg_pred = [sum(x)
                                                    for x in zip(*pred_list)]
                                        max_index = np.argmax(avg_pred, axis=1)
                                        max_value = np.max(avg_pred, axis=1)
                                        pred_list.clear()

                                        print(HumanNames)
                                        print(avg_pred)

                                        if confidence_thrushhold <= max_value / num_frames:

                                            # try to do a login
                                            usr = HumanNames[max_index[0]]
                                            print(usr)
                                            video_capture.release()
                                            cv2.destroyAllWindows()
                                            self.signin(usr)
                                            continue

                                    if dubug_mode:
                                        # boxing face
                                        cv2.rectangle(
                                            frame, (bb[i][0], bb[i][1]), (bb[i][2], bb[i][3]), (0, 255, 0), 2)

                                        # plot result idx under box
                                        text_x = bb[i][0]
                                        text_y = bb[i][3] + 20

                                        for H_i in HumanNames:
                                            if HumanNames[best_class_indices[0]] == H_i:
                                                result_names = HumanNames[best_class_indices[0]]
                                                cv2.putText(frame, result_names, (text_x, text_y), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                                            1, (0, 0, 255), thickness=1, lineType=2)

                        if dubug_mode and not self.bot.check_user_logedin():
                            cv2.imshow('Video', frame)
                        cv2.waitKey(1)

            # outside while true

    def signin(self, usr):
        users = self.bot.return_users()
        for u in users:
            if u[2].lower() == usr.lower():
                user_obj = user(
                    _id_arg=u[0], _super_arg=u[1], username_arg=u[2], password_arg=u[3])
                self.bot.update_current_user(user_obj)

    def face_recog_prompt(self):
        self.bot.text_action("Please face the camera So i can log you in.")

    def checks(self):
        if not self.checked:
            self.checked = True
            self.t = Timer(20.0, self.check_a_r)
            self.t.start()

    def check_a_r(self):
        cur_time = datetime.now().strftime("%H:%M")
        r = requests.get("http://mshahzaib.pythonanywhere.com/alarm/get")
        alarms = json.loads(r.text)["alarms"]

        r = requests.get("http://mshahzaib.pythonanywhere.com/reminder/get")
        reminders = json.loads(r.text)["reminders"]

        for a in alarms:
            if a[1] == cur_time:
                song = AudioSegment.from_mp3("a.mp3")
                play(song)

        for rem in reminders:
            if rem[1] == cur_time:
                self.bot.text_action("Reminder: " + rem[2])
                song = AudioSegment.from_mp3("a.mp3")
                play(song)

        self.checked = False


class user():

    def __init__(self, _id_arg, _super_arg, username_arg, password_arg):
        self._id = _id_arg
        self._super = _super_arg
        self.username = username_arg
        self.password = password_arg


if __name__ == "__main__":

    # check if front is running
    try:
        requests.get("http://localhost:8080", {"text": "Hello"})
    except Exception as e:
        print("Please run the 'front' first")
        

    test_user = user(_id_arg=1, _super_arg="yes",
                     username_arg="Admin", password_arg="pass123")

    h = Head(test_user)
    h.start()
