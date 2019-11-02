# train or predict displacement of tumor
# breast set:
# To run, python train.py --type=breast --train_data=. --pretrained_file=ck1.h5 --mode=connet_to_unity_weight
# python train.py --type=breast --train_data=disps --checkpoint=ck1.h5 --mode=train
# python train.py --type=breast --train_data=disps --pretrained_file=ck1.h5 --mode=train
# tumor set
# python train.py --type=tumor --train_data=tumor --checkpoint=tumor.h5 --mode=train
# python train.py --type=tumor --train_data=tumor --pretrained_file=tumor.h5 --mode=train
# when there is checkpoint already, don't need checkpoint. checkpoint is for 
# creating a new checkpoint

# cp4.h5, 40 hidden unit: 472us/sample - loss: 0.0097 - mean_absolute_error: 0.0396 - mean_squared_error: 0.0097 - val_loss: 0.0102 - val_mean_absolute_error: 0.0404 - val_mean_squared_error: 0.0102
# cp5.h5, 60 hidden unit: 2668/2668 [==============================] - 2s 679us/sample - loss: 0.0068 - mean_absolute_error: 0.0330 - mean_squared_error: 0.0068 - val_loss: 0.0067 - val_mean_absolute_error: 0.0329 - val_mean_squared_error: 0.0067
# cp6.h5, 2 hidden layer, each of which has 60 hidden unit. 2668/2668 [==============================] - 2s 593us/sample - loss: 0.0038 - mean_absolute_error: 0.0252 - mean_squared_error: 0.0038 - val_loss: 0.0037 - val_mean_absolute_error: 0.0254 - val_mean_squared_error: 0.0037
# cp7.h5, 2 hidden layer, first layer has 90 hidden unit, second layer has 60 hidden unit.

import argparse
import glob
import numpy as np
import os
import pdb
import random
import socket
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras import layers
import timeit
import sys
sys.path.insert(0, 'F:/Research/FEA simulation for NN/stl')
import generate_scenario
import manipulate_abaqus_file

def breast_model(point_num, col_num):
  model = keras.Sequential([
    layers.Flatten(input_shape=(1, 3)),
    layers.Dense(90, activation=tf.nn.relu),
    layers.Dense(60, activation=tf.nn.relu),
    layers.Dense(point_num * col_num)
  ])

  optimizer = tf.keras.optimizers.Adam(0.00001)

  model.compile(loss='mse',
                optimizer=optimizer,
                metrics=['mean_absolute_error', 'mse'])
  return model

def tumor_model(point_num, col_num):
  model = keras.Sequential([
    layers.Flatten(input_shape=(1, 3)),
    layers.Dense(30, activation=tf.nn.relu),
    layers.Dense(point_num * col_num)
  ])

  optimizer = tf.keras.optimizers.Adam(0.00001)

  model.compile(loss='mse',
                optimizer=optimizer,
                metrics=['mean_absolute_error', 'mse'])
  return model

def read(filename):
  with open(filename, "r") as file:
    data = file.readlines()
  with open(filename, "r") as file:
    num_lines = len(data)
    position = np.zeros([num_lines, 3])
    index = 0
    for line in file:
      text = line.strip().split(' ')
      position[index][0] = float(text[0])
      position[index][1] = float(text[1])
      position[index][2] = float(text[2])
      index += 1

  return position

def conv_to_string(data):
  res = ""
  if data.shape[0] == 1:
    for idx, temp in enumerate(data[0]):
      if idx == len(data[0]) - 1:
        res += str(temp)
      else:
        res += str(temp) + ','
  elif data.shape[1] == 3:
    for idx, temp in enumerate(data):
      if idx == data.shape[0] - 1:
        res += str(temp[0]) + ',' + str(temp[1]) + ',' + str(temp[2])
      else:
        res += str(temp[0]) + ',' + str(temp[1]) + ',' + str(temp[2]) + ','
  return res

# send data displacement above threshold
def filter_out_data(data, threshold):
  res = ""
  
  data_reshape = data.reshape(data.shape[1] // 3, 3)
  mag = np.sum(np.abs(data_reshape)**2,axis=1)**(1./2)
  for idx, temp in enumerate(data_reshape):
    if mag[idx] < threshold and idx != data_reshape.shape[0] - 1:
      continue
    if idx == data_reshape.shape[0] - 1:
   #   pdb.set_trace()
      res += str(idx) + ',' + str(temp[0]) + ',' + str(temp[1]) + ',' + str(temp[2])
    else:
      res += str(idx) + ',' + str(temp[0]) + ',' + str(temp[1]) + ',' + str(temp[2]) + ','
  return res

# conver the string to the data format in NN
# args:
# data: string like '1,2,3'
# returns:
# numpy array
def conv_to_weightpredc(data):
  data_float = data.split(',')
  try:
    len(data_float) == 3
  except:
    print('input must have 3 numbers')
  res = np.zeros((1, 1, 3))
  res[0,0,0] = data_float[0]
  res[0,0,1] = data_float[1]
  res[0,0,2] = data_float[2] 
  return res

def connect_to_unity(model, flag):
  host, port = '127.0.0.1', 25001
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.bind((host, port))
  sock.listen(5)
 # pdb.set_trace()
  while True:
    c, addr = sock.accept()
    data = c.recv(1024).decode('utf-8')
    if(flag == 'weight'):
        nnInput = conv_to_weightpredc(data)
    disp = model.predict(nnInput, batch_size=None, verbose=0)
    threshold = 0
    
    disp_str = filter_out_data(disp, threshold)
   
   # disp_str = conv_to_string(disp) 
    start = timeit.timeit()
    output_file = open('disp_prediction.txt', 'w')
    output_file.write(str(disp_str))
    output_file.close()
    end = timeit.timeit()
    ddd = disp_str.split(',')
    print(len(ddd))
  #  print(end - start)
  #  c.sendall(disp_str.encode('utf-8'))
   # c.sendall("OK".encode('utf-8'))
    c.close()    
    
# return the displacement on the surface. the surface indices are in order from small to large
def get_surface_disp(triangles, disp):
    res = []
    for tri in list(triangles):
        res.append(disp[tri])
    return res

def main(args):
  if args.type == 'breast': 
    disp_filenames = glob.glob('F:/Research/FEA simulation for NN/train_patient_specific/disps/*')
  elif args.type == 'tumor':
    disp_filenames = glob.glob('F:/Research/FEA simulation for NN/train_patient_specific/tumor/*')
  else:
    return
  random.shuffle(disp_filenames)
  num_files = len(disp_filenames)
  if num_files == 0:
    return
  if args.type == 'breast':
    surface_file = 'F:/Research/FEA simulation for NN/stl/Skin_Layer.face'
    breast_info = generate_scenario.GetInfoFromBreast('F:/Research/FEA simulation for NN/stl/Skin_Layer.ele', 'F:/Research/FEA simulation for NN/stl/Skin_Layer.node')
    triangles = breast_info.read_face_indices(surface_file)
    position = read(disp_filenames[0])
    point_num = triangles.shape[0]
  if args.type == 'tumor':
    point_num = 1
  col_num = 3
  nn_input = np.zeros([len(disp_filenames), 1, col_num])
  nn_output = np.zeros([len(disp_filenames), point_num * col_num])
  mode = args.mode
  if args.type == 'breast':
    model = breast_model(point_num, col_num)
  if args.type == 'tumor':
    model = tumor_model(point_num, col_num)
  if mode == 'train':
    inp_files = glob.glob('F:/Research/FEA simulation for NN/stl/Abaqus_outputs/weight/glandular_fat_10_90/*inp') 
    gravity = '** Name: GRAVITY-1   Type: Gravity\n'
    idx = 0
    for file in inp_files:
      name = os.path.basename(file)
      name = os.path.join(os.path.dirname(disp_filenames[0]), name.split('.')[0] + '.txt')
      if name in disp_filenames:
        abaqus = manipulate_abaqus_file.ReadAbaqusInput(file)
        _, direction = abaqus.read_gravity(gravity)            
        nn_input[idx, 0 : 1, :] = direction
        temp_pos = read(name)
        if args.type == 'breast':
          disp = np.array(get_surface_disp(triangles, temp_pos))  
        if args.type == 'tumor':
          disp = temp_pos
        nn_output[idx, :] = np.reshape(disp, point_num * col_num)
        idx += 1
    if args.pretrained_file != 'None':
      model.load_weights(args.pretrained_file)
      checkpoint = args.pretrained_file
    else:
      checkpoint = args.checkpoint
    checkpoint = ModelCheckpoint(checkpoint, monitor='loss', verbose=1, save_best_only=True)
    callbacks_list = [checkpoint]
    model.fit(nn_input, nn_output, epochs=10000, shuffle=True, validation_split=0.2, callbacks=callbacks_list, verbose=1)
 # model.evaluate()
  elif mode == 'infer':
    model.load_weights(args.pretrained_file)
    x = np.array([[[0, -20, 0], position[0]]])
    pdb.set_trace()
    res = model.predict(x, batch_size=None, verbose=0)
  elif mode == 'connet_to_unity_weight':
   # pdb.set_trace()
    model.load_weights(args.pretrained_file)
    flag = 'weight'
    connect_to_unity(model, flag)
    
if __name__ == "__main__":
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument('--train_data', help='Path file for training.', type=str)
  arg_parser.add_argument('--model_dir', help='The dir to save/load the model.', type=str)
  arg_parser.add_argument('--batch_size', help='Batch size.', type=int, default=64)
  arg_parser.add_argument('--checkpoint', help='Path file for checkpoint.', type=str)
  arg_parser.add_argument(
      '--mode', help='One of 3 modes: train, eval, infer or connet_to_unity.', type=str, default='train')
  arg_parser.add_argument(
      '--pretrained_file', help='load the pretrained weights', type=str, default='None')
  arg_parser.add_argument('--type', help='tumor or breast', type=str)
  args = arg_parser.parse_args()
  main(args)