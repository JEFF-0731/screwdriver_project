# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.


python 3.6
pip install tensorflow-gpu==2.6.0
pip install keras==2.6.0
pip install opencv-python==3.4.2.16
pip install matplotlib==3.3.4

"""
import numpy as np
import os
# import cv2
from sklearn.model_selection import train_test_split  # pip install scikit-learn
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import models
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.preprocessing.image import load_img
import tensorflow as tf
import os


class LearningRateTracker(keras.callbacks.Callback):
    def __init__(self):
        self._lr = list()

    def on_epoch_end(self, epoch, logs=None):
        optimizer = self.model.optimizer
        self._lr.append(tf.keras.backend.get_value(optimizer.lr))
        print(f'Epoch {epoch + 1}: Learning rate is {tf.keras.backend.get_value(optimizer.lr)}.\n')

    def show_train_learningRate(self):
        plt.plot(self._lr)
        plt.title('learningRate')
        plt.ylabel('learningRate')
        plt.xlabel('Epoch')
        plt.legend(['train', 'validation'], loc='upper left')
        plt.savefig('LearningRate.png')
        plt.show()


# os.environ['']
# =============================================================================
from keras.utils import np_utils

# =============================================================================
config = tf.compat.v1.ConfigProto()
gpus = tf.config.experimental.list_physical_devices('GPU')
os.environ["CUDA_VISIBLE_DEVICES"] = '0'
session = tf.compat.v1.Session(config=config)

epochs = 150  # 訓練的次數
batch_size = 18
img_rows = None  # 驗證碼影像檔的高
img_cols = None  # 驗證碼影像檔的寬
# digits_in_img = 6 #驗證碼影像檔中有幾位數
x_list = list()  # 存所有驗證碼數字影像檔的array
y_list = list()  # 存所有的驗證碼數字影像檔array代表的正確數字
x_train = list()  # 存訓練用驗證碼數字影像檔的array
y_train = list()  # 存訓練用驗證碼數字影像檔array代表的正確數字
x_test = list()  # 存測試用驗證碼數字影像檔的array
y_test = list()  # 存測試用驗證碼數字影像檔array代表的正確數字


def split_digits_in_img(img_array, x_list, y_list=None):  # 副函式：分割及儲存驗證碼
    #    for i in range(digits_in_img):
    #        step = img_cols // digits_in_img                                        #step=圖片總寬度除六
    #     y_list.append(img_filename[:2])                                              #將圖片正確數字(檔名)存進 y_list
    x_list.append(img_array)  # 將圖片存進x_list


input_filepath = './trainingset/1205_Trainning'
file_list = sorted(os.listdir(input_filepath))  # 获取文件名列表.
print(f'file_list = {file_list}')
for classnumber in file_list:
    img_filenames = os.listdir(f'{input_filepath}/{classnumber}')
    count = 0  # os.listdir() 方法用于返回指定的文件夹包含的文件或文件夹的名字的列表
    for img_filename in img_filenames:
        count += 1
        if '.png' not in img_filename:  # 只讀取PNG檔
            continue
        # img = load_img('./output_file(00)/{0}/{1}'.format(classnumber, img_filename), color_mode='rgb', target_size=(224, 224, 3)) #將圖片依序以灰階讀取
        img = load_img('{0}/{1}/{2}'.format(input_filepath, classnumber, img_filename), color_mode='grayscale',
                       target_size=(112, 112, 1))  # 將圖片依序以灰階讀取
        img_array = img_to_array(img)  # 將圖片轉換成數值
        img_rows, img_cols, _ = img_array.shape  # 將圖片長寬分別儲存在img_rows, img_cols,
        # print(img_array.shape)
        y_list.append(classnumber[:2])  # 將圖片正確數字(檔名)存進 y_list
        split_digits_in_img(img_array, x_list, y_list)  # 呼叫 副函式：分割及儲存驗證碼
    print(f'{classnumber} is ok --> 有{count}張')
x_train, x_test, y_train, y_test = train_test_split(x_list, y_list, test_size=0.1,
                                                    stratify=y_list)  # , stratify=y_list随机划分训练集和测试集
# print(x_train)
# print(y_train)

y_train = keras.utils.to_categorical(y_train)  # 將y_list 轉換成categorical形式
y_test = keras.utils.to_categorical(y_test)

# =============================================================================
# y_train_onehot = np_utils.to_categorical(y_train)
# y_test_onehot = np_utils.to_categorical(y_test)
# =============================================================================

# =============================================================================
# if os.path.isfile('cnn_model.h5'):                                              #檢測是否已有模型
#     model = models.load_model('cnn_model.h5')                                   #將該模型導入
#     print('Model loaded from file.')
# else:                                                                           #否則：建立新模型
# =============================================================================


model = models.Sequential()
# 創建模型
model.add(layers.Conv2D(input_shape=(112, 112, 1), filters=64, kernel_size=(4, 4), padding="same", activation="relu"))
model.add(layers.Conv2D(filters=64, kernel_size=(3, 3), padding="same", activation="relu"))
model.add(layers.MaxPool2D(pool_size=(3, 3), strides=(2, 2)))
model.add(layers.Dropout(rate=0.3))  # 0
model.add(layers.Conv2D(filters=128, kernel_size=(3, 3), padding="same", activation="relu"))
model.add(layers.Conv2D(filters=128, kernel_size=(3, 3), padding="same", activation="relu"))
model.add(layers.MaxPool2D(pool_size=(3, 3), strides=(2, 2)))
model.add(layers.Dropout(rate=0.2))  # 0
model.add(layers.Conv2D(filters=256, kernel_size=(3, 3), padding="same", activation="relu"))
model.add(layers.Conv2D(filters=256, kernel_size=(3, 3), padding="same", activation="relu"))
model.add(layers.Conv2D(filters=256, kernel_size=(3, 3), padding="same", activation="relu"))
model.add(layers.Conv2D(filters=256, kernel_size=(3, 3), padding="same", activation="relu"))
model.add(layers.MaxPool2D(pool_size=(3, 3), strides=(2, 2)))
model.add(layers.Dropout(rate=0.2))  # 0
model.add(layers.Conv2D(filters=512, kernel_size=(3, 3), padding="same", activation="relu"))
model.add(layers.Conv2D(filters=512, kernel_size=(3, 3), padding="same", activation="relu"))
model.add(layers.Conv2D(filters=512, kernel_size=(3, 3), padding="same", activation="relu"))
model.add(layers.Conv2D(filters=512, kernel_size=(3, 3), padding="same", activation="relu"))
model.add(layers.MaxPool2D(pool_size=(3, 3), strides=(2, 2)))
model.add(layers.Dropout(rate=0.2))  # 5
model.add(layers.Conv2D(filters=512, kernel_size=(3, 3), padding="same", activation="relu"))
model.add(layers.Conv2D(filters=512, kernel_size=(3, 3), padding="same", activation="relu"))
model.add(layers.Conv2D(filters=512, kernel_size=(3, 3), padding="same", activation="relu"))
model.add(layers.Conv2D(filters=512, kernel_size=(3, 3), padding="same", activation="relu"))
model.add(layers.MaxPool2D(pool_size=(3, 3), strides=(2, 2)))

model.add(layers.Flatten())
model.add(layers.Dense(units=4096, activation="relu"))
model.add(layers.Dropout(rate=0.5))  # 6
model.add(layers.Dense(units=4096, activation="relu"))
model.add(layers.Dense(units=17, activation="softmax"))  # 這是類別數
# 全連接層 (輸出空間的維數,activation)
print('New model created.')  # 全連接層 (輸出空間的維數,activation)

model.compile(loss=keras.losses.categorical_crossentropy,
              optimizer=keras.optimizers.Adam(learning_rate=0.000001, beta_1=0.9, beta_2=0.999), metrics=['accuracy'])
# model.compile 編譯模型（optimizer =優化器，loss =損失函數， metrics= [“準確率”]）
# model.fit(np.array(x_train), np.array(y_train), batch_size=digits_in_img, epochs=epochs, verbose=1, validation_data=(np.array(x_test), np.array(y_test)))
# =============================================================================
checkpoint_filepath = os.path.sep.join(['checkpoint',
                                        "weights-{epoch:03d}-{loss:.9f}-{val_accuracy:.4f}.h5"])
model_checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_filepath,
    save_weights_only=False,
    monitor='loss',
    mode='min',
    save_best_only=True)

lr_tracker = LearningRateTracker()
with tf.device('/cpu:0'):
   x_train = tf.convert_to_tensor(x_train, np.float32)
   y_train = tf.convert_to_tensor(y_train, np.float32)
train_history = model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, verbose=1,
                          callbacks=[model_checkpoint_callback, lr_tracker],
                          validation_data=(np.array(x_test), np.array(y_test)), shuffle=True)
import matplotlib.pyplot as plt


def show_train_history(train_history, title, train_metric, val_metric):
    plt.plot(train_history.history[train_metric])
    plt.plot(train_history.history[val_metric])
    plt.title(title)
    plt.ylabel(train_metric)
    plt.xlabel('Epoch')
    plt.legend(['train', 'validation'], loc='upper left')
    plt.savefig(f'{title}.png')
    plt.show()


show_train_history(train_history, 'Accuracy', 'accuracy', 'val_accuracy')
show_train_history(train_history, 'Loss', 'loss', 'val_loss')
lr_tracker.show_train_learningRate()
# =============================================================================

loss, accuracy = model.evaluate(np.array(x_test), np.array(y_test), verbose=1)  # 評估模型(verbose：0或1。詳細模式。 0 =靜音，1 =進度欄。)
# print('Test loss:', loss)
# print('Test accuracy:', accuracy)

model.save('model1124.h5')
print(model.summary())