import os
import pickle
import time

import cv2
import numpy as np
from tensorflow.keras.applications.mobilenet import preprocess_input

from roi.model_util import DeepModel


class ImageClassifier:
    def __init__(self):
        self.all_skus = {}
        self.model = DeepModel()
        self.predict_time = 0
        self.time_search = 0
        self.count_frame = 0
        self.top_k = 5
        self.test_images = 'roi_test'
        self.path_t = 'roi_data'

    def new_class(self):
        self.test_paths = os.listdir(self.test_images)
        self.image_class = dict()
        self.class_image = dict()
        for f in self.test_paths:
            self.image = f.split(".")[0]
            self.image_class[self.image] = [self.image]
            self.class_image[self.image] = self.image
            classifier.add_img(os.path.join(self.test_images, f), f)

    def predict_dist(self):
        for self.data_img in os.listdir(self.path_t):
            frame = cv2.imread(os.path.join(self.path_t, self.data_img))
            name, dist = classifier.predict(frame)
            name = name.split(".")[0]
            data_name = self.data_img.split(".")[0]
            if dist >= 0.6:
                print(self.class_image[name], dist, "OK")
                classifier.add_img(os.path.join(self.path_t, self.data_img), self.data_img)
                self.image_class[self.class_image[name]].append(data_name)
                self.class_image[data_name] = self.class_image[name]
            else:
                print(name, dist, "MISS")
    def extract_features_from_img(self, cur_img):
        cur_img = cv2.resize(cur_img, (224, 224))
        img = preprocess_input(cur_img)
        img = np.expand_dims(img, axis=0)
        feature = self.model.extract_feature(img)
        return feature

    def predict(self, img):
        self.count_frame += 1
        before_time = time.time()
        target_features = self.extract_features_from_img(img)
        self.predict_time += time.time() - before_time
        max_distance = 0
        result_dish = 0
        pr_time = time.time()
        for dish, features_all in self.all_skus.items():
            for features in features_all:
                cur_distance = self.model.cosine_distance(target_features, features)
                cur_distance = cur_distance[0][0]
                if cur_distance > max_distance:
                    max_distance = cur_distance
                    result_dish = dish
        return result_dish, max_distance

    def add_img(self, img_path, id_img):
        img = cv2.imread(img_path)
        cur_img = img
        feature = self.extract_features_from_img(cur_img)
        if id_img not in self.all_skus:
            self.all_skus[id_img] = []
        self.all_skus[id_img].append(feature)
        return feature

    def remove_by_id(self, id_img):
        if id_img in self.all_skus:
            self.all_skus.pop(id_img)

    def remove_all(self):
        self.all_skus.clear()

    def add_img_from_pickle(self, id_img, pickle_path):
        res = pickle.load(open(pickle_path, 'rb'))
        self.all_skus[id_img] = res

    def get_additional_info(self):
        json_res = {}
        json_res["Extract features, time"] = self.predict_time
        json_res["Find nearest, time"] = self.time_search
        json_res["Count frame"] = self.count_frame
        json_res["RPS"] = self.count_frame / (self.predict_time + self.time_search)
        return json_res

classifier = ImageClassifier()
classifier.new_class()
classifier.predict_dist()