# -*- coding: utf-8 -*-
"""klasifikasimangga_viskimipynb_80.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1u1tQRJtCKwPluYBk60Q51TeLspXGnXf9
"""

#mengimport Library yang dibutuhkan
import numpy as np
import matplotlib.pyplot as plt
import os
import cv2
import random
import warnings
import keras
import tensorflow as tf
from google.colab import drive
import warnings
warnings.filterwarnings("ignore")
from PIL import Image
import io
import ipywidgets as widgets

#Menyambungkan google drive ke google colab
from google.colab import drive
drive.mount('/content/drive')

#menetukan sumber lokasi dataset di dalam drive
data_path='/content/drive/MyDrive/Skripsi/Dataset'
categories=os.listdir(data_path)
labels=[i for i in range(len(categories))]

label_dict=dict(zip(categories,labels)) #empty dictionary
print(label_dict)
print(categories)
print(labels)

#Step1 Membuat data dan segala konfigurasinya
#Membuat path dataset
os.chdir('/content')
ROOT_PATH = os.getcwd()
DATASET_PATH = os.path.join(ROOT_PATH, '/content/drive/MyDrive/Skripsi/Dataset')

img_all = [] #Menampung semua image beserta label

#augmentasi data
IMG_SIZE = 200

rasio_training = 80 #Menyatakan prosentase data training dari dataset dalam satuan persen
#SKENARIO_DATASET_PATH = os.path.join(DATASET_PATH)
print(DATASET_PATH)
#print(SKENARIO_DATASET_PATH)

CATEGORIES = os.listdir(DATASET_PATH) #Menentukan kategori/kelas berdasarkan nama folder dataset yang ada
num_classes = len(CATEGORIES) #Menghitung jumlah kelas

for category in CATEGORIES:
  path = os.path.join(DATASET_PATH,category) #Menambah path dari category
  for img in os.listdir(path): #untuk setiap gambar yang ada di folder
    img_array = cv2.imread(os.path.join(path,img), cv2.IMREAD_GRAYSCALE)
    try:
        new_img_array = cv2.resize(img_array,(IMG_SIZE,IMG_SIZE)) #Melakukan resize image
        img_all.append([new_img_array,category]) #img_all berisi image dan kategori
        print(len(img_all))
    except Exception as e:
            print('Exception:',e)
            #if any exception rasied, the exception will be printed here. And pass to the next image

#Step 2 : Mengacak data dan membagi porsi data training dan data testing
random.shuffle(img_all) #Mengacak susunan dataset

n_dataset = len(img_all) #Mengetahui jumlah seluruh dataset
n_training = int(round(rasio_training/100 * n_dataset)) #Menghitung jumlah data training

img_lablel_training = img_all[:n_training] #img training (masih berupa list) list masih termasuk img dan labelnya
img_lablel_testing = img_all[n_training:] #img testing (masih berupa list) list masih termasuk imgdan labelnya

#Mensplit antara image dan label dari data training
img_training = []
lbl_training = []

for data in img_lablel_training:
  img_training.append(data[0])
  lbl_training.append(data[1])

#Mensplit antara image dan label dari data testing
img_testing = []
lbl_testing = []

for data in img_lablel_testing:
  img_testing.append(data[0])
  lbl_testing.append(data[1])

img_training_array = np.array(img_training)
img_testing_array = np.array(img_testing)

print("Jumlah data training : %d " % (img_training_array.shape[0]))
print("Jumlah data testing : %d " % (img_testing_array.shape[0]))

from tensorflow import keras
#Step 3 : Normalisasi image sehingga nilai maksimal pixel dibuat 1 dan melakukan one hot encodinguntuk label
lbl_training_numeris = [] #Menyimpan label training secara numeris
lbl_testing_numeris = [] #Menyimpan label testing secara numeris

for data in lbl_training:
  #Convert label to index label
  lbl_training_numeris.append(CATEGORIES.index(data))

for data in lbl_testing:
  #Convert label to index label
  lbl_testing_numeris.append(CATEGORIES.index(data))

#Konversi label numeris menjadi bentuk one hot
lbl_training_one_hot = keras.utils.to_categorical(lbl_training_numeris,num_classes)
lbl_testing_one_hot = keras.utils.to_categorical(lbl_testing_numeris,num_classes)

#Mengubah nilai pada array menjadi float
img_training_array_f = img_training_array.astype('float32')
img_testing_array_f = img_testing_array.astype('float32')

#Normalisasi img array
img_training_array_f /= 255
img_testing_array_f /= 255

#Step 4: Mengubah gambar color menjadi grayscale
img_training_array_f_2D = img_training_array_f.reshape(-1,IMG_SIZE,IMG_SIZE,1)
img_testing_array_f_2D = img_testing_array_f.reshape(-1,IMG_SIZE,IMG_SIZE,1)

#Step 5: Membangun Model
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D

model = Sequential()

#Conv2D(filter,kernel_size,padding,input_shape)
model.add(Conv2D(32,(3,3),padding='same',input_shape=img_training_array_f_2D.shape[1:]))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.5))
model.add(Conv2D(64,(3,3),padding='same'))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.5))

model.add(Flatten())
model.add(Dense(128, activation = 'relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes))
model.add(Activation('softmax'))

model.summary()

# from tensorflow.keras.applications import VGG16

# base_model = VGG16(weights = "imagenet", include_top=False, input_shape=img_training_array_f_2D.shape[1:])
# modelvgg = Sequential()

# modelvgg.add(base_model)
# modelvgg.add(Flatten())
# modelvgg.add(Dense(128, activation='relu',  name='dense'))
# modelvgg.add(Dropout(0.5))
# modelvgg.add(Dense(len(classes), activation='softmax',  name='predictions'))

# modelvgg.summary()

#Step 6: Melatih model

import time
#Hyperparameter
learning_rate = 0.01
opt = keras.optimizers.Adam(lr =learning_rate) #Optimizer (Gradient Descent Optimier, adaptive learning rate)
model.compile(loss='categorical_crossentropy',optimizer=opt,metrics=['accuracy']) #yang diukur hanya akurasi
#model.compile(loss='categorical_crossentropy',optimizer=opt,metrics=[tf.keras.metrics.SensitivityAtSpecificity(0.5)]) #yang diukur hanya akurasi
batch_size = 32 #Ambil 5 data dari dataset untuk satu kali iterasi
epochs = 15 #dataset dimasukkan ke dalam model sebanyak 30 kali. 1 epoch itu artinya 1 kali prosessemua dataset ditrainingkan ke model
start = time.time() #waktu mulai training

history = model.fit(img_training_array_f_2D,lbl_training_one_hot,batch_size=batch_size,
                    epochs=epochs,validation_data=(img_testing_array_f_2D,lbl_testing_one_hot),
                    shuffle=True) #proses melatih model

end = time.time() #waktu selesai training

print("Model membutuhkan {:2.0f} detik untuk dilatih".format((end-start)))

#Step 7: Melihat history dari proses training
def plot_model_history(model_history):
  plt.subplot(2 , 1, 1)
  #fungsi untuk melihat plot history training
  #Untuk melihat akurasi dan akurasi validasi
  plt.plot(model_history.history['accuracy'])
  plt.plot(model_history.history['val_accuracy'])
  plt.title('Akurasi Model')
  plt.ylabel('Akurasi')
  plt.xlabel('Epoch')
  plt.legend(['by data training','by data testing'], loc= 'lower right')
  #plt.show()

  plt.subplot(2 , 1, 2)
  #Untuk melihat loss
  plt.plot(model_history.history['loss'])
  plt.plot(model_history.history['val_loss'])
  plt.title('Loss Model')
  plt.ylabel('Loss')
  plt.xlabel('Epoch')
  plt.legend(['by data training','by data testing'], loc= 'upper right')
  #plt.show()
  plt.tight_layout()

plot_model_history(history)

#Step 8 - Prediction
def show_image_prediction(i,prediction_array,true_label,img):
  #fungsi untuk menampilkan prediksi dari sebuah gambar
  predict_array = prediction_array[i]
  tr_label = true_label[i]
  img = img[i]

  plt.grid(False)
  plt.xticks([])
  plt.yticks([])
  plt.imshow(img, cmap=plt.cm.binary)
  predicted_label = np.argmax(predict_array) #mengetahui index node output mana yang bernilai paling tinggi

  if predicted_label == tr_label:
    warna = "blue"
  else:
    warna = "red"

  plt.xlabel("{label} \nconf_lvl: {conf_level:2.0f}% \n({seharusnya})".format(label=CATEGORIES[predicted_label],
                                                                              conf_level=100*np.max(predict_array),seharusnya=CATEGORIES[tr_label]),color=warna)

NEW_CATEGORIES = [x[0] for x in CATEGORIES] #Untuk mengambil inisial dari nama kategori

def show_value_prediction(i,prediction_array,true_label):
  y = [] #y = [true,predict]
  predict_array = prediction_array[i]
  tr_label = true_label[i]

  plt.grid(False)
  plt.xticks(range(num_classes),NEW_CATEGORIES)
  plt.yticks([])
  plt.xlabel("Kelas")
  plt.ylabel("Conf. Level")
  thisplot = plt.bar(range(num_classes),predict_array,color="#777777")
  for index,value in enumerate(predict_array):
    plt.text(index,value,"{conf_level:2.0f}%".format(conf_level=value*100))
  plt.ylim([0,1])
  predicted_label = np.argmax(predict_array)

  y.append(NEW_CATEGORIES[tr_label]) #y_true
  y.append(NEW_CATEGORIES[predicted_label]) #y_predict
  thisplot[predicted_label].set_color("red")
  thisplot[tr_label].set_color("blue")
  return y

predictions = model.predict(img_testing_array_f_2D) #Mengujinya dengan image test (testing set) yang sudah berbentuk float

i = 0
plt.figure(figsize=(20,10)) #membuat gambar
plt.subplot(1,2,1)
show_image_prediction(i, predictions, lbl_training_numeris, img_testing)
plt.subplot(1,2,2)
y = show_value_prediction(i, predictions, lbl_testing_numeris) #Menghasilkan y_true sama y_predict

#Jika data tidak terlalu banyak
#Multi predict
import math

n_data_testing = img_testing_array.shape[0]
n_kolom_display = 2 #Jumlah kolom yang ditampilkan
n_baris_display = math.ceil(n_data_testing / n_kolom_display) #Jumlah baris yang ditampilkan sebelum ditambah modulo
n_modulo = n_data_testing % n_kolom_display #jumlah sisa gambar yang akan ditampilkan

plt.figure(figsize=(2*2*n_kolom_display,2*n_baris_display))
#n_data_testing
y_final = []

#Jika data tidak terlalu banyak
for i in range(n_data_testing):
  plt.subplot(n_baris_display , 2*n_kolom_display, 2*i + 1)
  show_image_prediction(i,predictions,lbl_testing_numeris,img_testing)
  plt.subplot(n_baris_display, 2*n_kolom_display, 2*i + 2)
  y = show_value_prediction(i,predictions,lbl_testing_numeris)
  y_final.append(y)
plt.tight_layout()

#Untuk mencari nilai result groundtruth dan hasil prediksi
Y_true = []
Y_predict = []
for y in y_final:
  Y_true.append(y[0])
  Y_predict.append(y[1])

#Membuat confusion matrix
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
CATEGORIES_FOR_CM = NEW_CATEGORIES
CATEGORIES_FOR_CM.sort()

cm = confusion_matrix(Y_true, Y_predict)
print(classification_report(Y_true, Y_predict))
sns.heatmap(cm, annot=True)

model.save('model.h5')
from google.colab import files
files.download("model.h5")