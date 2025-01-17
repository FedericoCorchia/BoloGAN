import json
import numpy as np

import os, sys
import time
import math
from resource import *

sys.path.append('../common/')

from pdb import set_trace

import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras import activations
from tensorflow.keras.models import Model
from functools import partial
tf.keras.backend.set_floatx('float32')

from VoxInputParameters import VoxInputParameters
from TrainingInputParameters import TrainingInputParameters
from DataParameters import DataParameters
from DataReader import DataLoader

if 'fix_seed' in os.environ and os.environ['fix_seed'].lower() == 'true':
  print('Fix random seed')
  import random, numpy, tensorflow
  random.seed(10)
  numpy.random.seed(10)
  tensorflow.random.set_seed(10)

class WGANGP():
  def __init__(self, voxInputs, ganParameters):
    self.voxInputs = voxInputs
    self.ganParameters = ganParameters
    
    self.exp_min = 0 
    self.exp_max = 0

    # Construct D and G models
    self.G = self.make_generator_functional_model() 
    self.D = self.make_discriminator_model()

    # Construct D and G losses
    #self.gradient_penalty = gradient_penalty
    #self.D_loss = D_loss
    #self.G_loss = G_loss

    # Construct D and G optimizers
    self.generator_optimizer = tf.optimizers.Adam(learning_rate=self.ganParameters.G_lr, beta_1=self.ganParameters.G_beta1)
    self.discriminator_optimizer = tf.optimizers.Adam(learning_rate=self.ganParameters.D_lr, beta_1=self.ganParameters.D_beta1)

    # Prepare for check pointing
    self.saver = tf.train.Checkpoint(generator_optimizer=self.generator_optimizer,
                               discriminator_optimizer=self.discriminator_optimizer,
                               generator=self.G,
                               discriminator=self.D)

    self.tf_batchsize = tf.constant(self.ganParameters.batchsize, dtype=tf.int32)
    self.tf_n_disc = tf.constant(self.ganParameters.n_disc, dtype=tf.int32)
 
  def make_generator_functional_model(self):
    initializer = tf.keras.initializers.he_uniform()
    bias_node = True
    noise = layers.Input(shape=(self.ganParameters.latent_dim,), name="Noise")
    condition = layers.Input(shape=(self.ganParameters.conditional_dim,), name="mycond")
    con = layers.concatenate([noise,condition])

    if (self.ganParameters.activationFunction == "ReLU"):
      if (self.ganParameters.useBatchNormalisation):
        #UltraLow
        G = layers.Dense(self.ganParameters.generatorLayers[0], use_bias=bias_node, kernel_initializer=initializer, bias_initializer='zeros')(con)
        G = layers.BatchNormalization()(G)
        G = layers.LeakyReLU(alpha=0)(G)
        G = layers.Dense(self.ganParameters.generatorLayers[1], use_bias=bias_node, kernel_initializer=initializer, bias_initializer='zeros')(G)
        G = layers.BatchNormalization()(G)
        G = layers.LeakyReLU(alpha=0)(G)
        G = layers.Dense(self.ganParameters.generatorLayers[2], use_bias=bias_node, kernel_initializer=initializer, bias_initializer='zeros')(G)
        G = layers.BatchNormalization()(G)
        G = layers.LeakyReLU(alpha=0)(G)
        G = layers.Dense(self.ganParameters.nvoxels, use_bias=bias_node, kernel_initializer=initializer, bias_initializer='zeros')(G)
        G = layers.LeakyReLU(alpha=0)(G)
      else:
        #Pions
        G = layers.Dense(self.ganParameters.generatorLayers[0], activation="relu", use_bias=bias_node, kernel_initializer=initializer, bias_initializer='zeros')(con)
        G = layers.Dense(self.ganParameters.generatorLayers[1], activation="relu", use_bias=bias_node, kernel_initializer=initializer, bias_initializer='zeros')(G)
        G = layers.Dense(self.ganParameters.generatorLayers[2], activation="relu", use_bias=bias_node, kernel_initializer=initializer, bias_initializer='zeros')(G)
        G = layers.Dense(self.ganParameters.nvoxels, activation="relu", use_bias=bias_node, kernel_initializer=initializer, bias_initializer='zeros')(G)

    elif (self.ganParameters.activationFunction == "swish"):
      #High12
      G = layers.Dense(self.ganParameters.generatorLayers[0], use_bias=bias_node, kernel_initializer=initializer, bias_initializer='zeros')(con)  
      G = layers.BatchNormalization()(G)
      G = layers.Activation(activations.swish)(G)
      G = layers.Dense(self.ganParameters.generatorLayers[1], use_bias=bias_node, kernel_initializer=initializer, bias_initializer='zeros')(G)
      G = layers.BatchNormalization()(G)
      G = layers.Activation(activations.swish)(G)
      G = layers.Dense(self.ganParameters.generatorLayers[2], use_bias=bias_node, kernel_initializer=initializer, bias_initializer='zeros')(G)
      G = layers.BatchNormalization()(G)
      G = layers.Activation(activations.swish)(G)
      G = layers.Dense(self.ganParameters.nvoxels, use_bias=bias_node, kernel_initializer=initializer, bias_initializer='zeros')(G)
      G = layers.BatchNormalization()(G)
      G = layers.Activation(activations.swish)(G)

    generator = Model(inputs=[noise, condition], outputs=G)
    generator.summary()
    return generator

  def make_discriminator_model(self):
    initializer = tf.keras.initializers.he_uniform()
    bias_node = True
    model = tf.keras.Sequential()
    model.add(layers.Dense(self.ganParameters.discriminatorLayers[0], use_bias=bias_node,
                           input_shape=(self.ganParameters.nvoxels + self.ganParameters.conditional_dim,),
                           kernel_initializer=initializer,
                           bias_initializer='zeros'))
    model.add(layers.ReLU())
    model.add(layers.Dense(self.ganParameters.discriminatorLayers[1], use_bias=bias_node,
                           input_shape=(self.ganParameters.discriminatorLayers[0],),
                           kernel_initializer=initializer,
                           bias_initializer='zeros'))
    model.add(layers.ReLU())
    model.add(layers.Dense(self.ganParameters.discriminatorLayers[2], use_bias=bias_node,
                           input_shape=(self.ganParameters.discriminatorLayers[1],),
                           kernel_initializer=initializer,
                           bias_initializer='zeros'))
    model.add(layers.ReLU())
    model.add(layers.Dense(1, use_bias=bias_node,
                           input_shape=(self.ganParameters.discriminatorLayers[2],),
                           kernel_initializer=initializer,
                           bias_initializer='zeros'))
    model.summary()
    return model

  @tf.function
  def gradient_penalty(self, f, x_real, x_fake, cond_label):
    alpha = tf.random.uniform([self.ganParameters.batchsize, 1], minval=0., maxval=1.)

    inter = alpha * x_real + (1-alpha) * x_fake
    with tf.GradientTape() as t:
      t.watch(inter)
      pred = self.D(tf.concat([inter, cond_label], 1))
    grad = t.gradient(pred, [inter])[0]
    
    slopes = tf.sqrt(tf.reduce_sum(tf.square(grad), axis=1))
    gp = self.ganParameters.lam * tf.reduce_mean((slopes - 1.)**2)
    return gp

  @tf.function
  def D_loss(self, x_real, cond_label): 
    z = tf.random.normal([self.ganParameters.batchsize, self.ganParameters.latent_dim], mean=0.5, stddev=0.5, dtype=tf.dtypes.float32)
    #x_fake = self.G(tf.concat([z, cond_label], 1))
    #x_fake = self.G(Noise=z, mycond=cond_label)
    x_fake = self.G(inputs=[z, cond_label])
    D_fake = self.D(tf.concat([x_fake, cond_label], 1))
    D_real = self.D(tf.concat([x_real, cond_label], 1))
    D_loss = tf.reduce_mean(D_fake) - tf.reduce_mean(D_real) + self.gradient_penalty(f = partial(self.D, training=True), x_real = x_real, x_fake = x_fake, cond_label=cond_label)
    return D_loss, D_fake

  @tf.function
  def G_loss(self, D_fake):
    G_loss = -tf.reduce_mean(D_fake)
    return G_loss

  def getTrainData_ultimate(self, n_epoch):
    true_batchsize = tf.cast(tf.math.multiply(self.tf_batchsize, self.tf_n_disc), tf.int64)
    n_samples = tf.cast(tf.gather(tf.shape(self.X), 0), tf.int64)
    n_batch = tf.cast(tf.math.floordiv(n_samples, true_batchsize), tf.int64)
    n_shuffles = tf.cast(tf.math.ceil(tf.divide(n_epoch, n_batch)), tf.int64)
    ds = tf.data.Dataset.from_tensor_slices((self.X, self.Labels))
    ds = ds.shuffle(buffer_size = n_samples).repeat(n_shuffles).batch(true_batchsize, drop_remainder=True).prefetch(2)
    self.ds = ds
    self.ds_iter = iter(ds)
    X_feature_size = tf.gather(tf.shape(self.X), 1)
    Labels_feature_size = tf.gather(tf.shape(self.Labels), 1)
    self.X_batch_shape = tf.stack((self.tf_n_disc, self.tf_batchsize, X_feature_size), axis=0)
    self.Labels_batch_shape = tf.stack((self.tf_n_disc, self.tf_batchsize, Labels_feature_size), axis=0)

  @tf.function
  def train_loop(self, X_trains, cond_labels): 
    for i in tf.range(self.tf_n_disc):
      with tf.GradientTape() as disc_tape:
        (D_loss_curr, D_fake) = self.D_loss(tf.gather(X_trains, i), tf.gather(cond_labels, i))
        gradients_of_discriminator = disc_tape.gradient(D_loss_curr, self.D.trainable_variables)
        self.discriminator_optimizer.apply_gradients(zip(gradients_of_discriminator, self.D.trainable_variables))

    last_index = tf.subtract(self.tf_n_disc, 1)
    with tf.GradientTape() as gen_tape:
      # Need to recompute D_fake, otherwise gen_tape doesn't know the history
      (D_loss_curr, D_fake) = self.D_loss(tf.gather(X_trains, last_index), tf.gather(cond_labels, last_index))
      G_loss_curr = self.G_loss(D_fake)
      gradients_of_generator = gen_tape.gradient(G_loss_curr, self.G.trainable_variables)
      self.generator_optimizer.apply_gradients(zip(gradients_of_generator, self.G.trainable_variables))
      return D_loss_curr, G_loss_curr


  def train(self, trainingInputs, dataParamaters):
    checkpoint_dir = trainingInputs.GAN_dir +'/%s/checkpoints_eta_%s_%s/' % (self.voxInputs.particle,self.voxInputs.eta_min,self.voxInputs.eta_max)
    if not os.path.exists(checkpoint_dir):
      os.makedirs(checkpoint_dir)

    print ('training started')
    print("Memory required before loading data: " + str(getrusage(RUSAGE_SELF).ru_maxrss))
    dl = DataLoader(self.voxInputs, dataParamaters)

    print("Memory required after loading data: " + str(getrusage(RUSAGE_SELF).ru_maxrss))

    D_loss_iter, G_loss_iter, Epochs = [], [], []
    time_iter, mem_iter = [], []

    if trainingInputs.loadFromBaseline:
      try:
        print("Try to load checkpoint from baseline folder %s" % (trainingInputs.loading_dir))
        self.saver.restore("%s/model_%s_region_%s" % (trainingInputs.loading_dir, self.voxInputs.particle,self.voxInputs.region))   
        #self.saver.save_counter=1
      except:
        print("Error while loading baseline checkpoint", sys.exc_info()[0])
        raise
    else:
      print("Train seed")

    if trainingInputs.start_epoch > 0:
      try:
        print("Try to load starting model %d" % (trainingInputs.start_epoch))
        iepoch = str(int((trainingInputs.start_epoch - 100000) / 2000 + 1))
        print ('convert trainingInputs.start_epoch ', trainingInputs.start_epoch, iepoch)
        self.saver.restore("%s/model-%s" % (checkpoint_dir, iepoch))
        D_loss_iter = np.loadtxt(checkpoint_dir + "/d_loss.txt").tolist()
        G_loss_iter = np.loadtxt(checkpoint_dir + "/g_loss.txt").tolist()
        trainingInputs.start_epoch = trainingInputs.start_epoch + 1
        
      except:
        print("Error while loading checkpoint", sys.exc_info()[0])
        raise

    ind_of_exp = 1

    if (trainingInputs.training_strategy == "All"):
      print("Training is done using all sample together") 
      self.exp_max = dataParamaters.max_expE
      self.exp_min = dataParamaters.min_expE
    elif (trainingInputs.training_strategy == "Sequential"):
      print("Sequential training, first sample trained for " + str(trainingInputs.epochsForFirstSample) + " epochs, additional samples added at intervals of " + str(trainingInputs.epochsForAddingASample) + " epochs") 
      self.exp_max = dataParamaters.exp_mid
      self.exp_min = dataParamaters.exp_mid

    for epoch in range(0,trainingInputs.start_epoch): 
      #after 50000, each 20000 it makes larger the reange
      if trainingInputs.training_strategy == "Sequential" and epoch >= trainingInputs.epochsForFirstSample  and (epoch-trainingInputs.epochsForFirstSample) % trainingInputs.epochsForAddingASample == 0: 
        if ind_of_exp == 0 :
          self.exp_max += 1
          ind_of_exp += 1
        elif ind_of_exp > 0:
          if self.exp_max <dataParamaters.max_expE: 
            self.exp_max += 1
            ind_of_exp = -ind_of_exp
        else :
          if self.exp_min > dataParamaters.min_expE:
            self.exp_min -= 1
            ind_of_exp = -ind_of_exp
          
    s_time = time.time()
    dur_train_loop = dur_getTrainData_ultimate = dur_convert = 0
    for epoch in range(trainingInputs.start_epoch, trainingInputs.max_epochs): 
      change_data = (epoch == trainingInputs.start_epoch)
      
      if trainingInputs.training_strategy == "Sequential" and epoch >= trainingInputs.epochsForFirstSample  and (epoch-trainingInputs.epochsForFirstSample) % trainingInputs.epochsForAddingASample == 0: 
        #after 50000, each 20000 it makes larger the reange
        if ind_of_exp == 0 :
          self.exp_max += 1
          change_data = True
          ind_of_exp += 1
        elif ind_of_exp > 0:
          if self.exp_max <dataParamaters.max_expE: 
            self.exp_max += 1
            change_data = True
            ind_of_exp = -ind_of_exp
        else :
          if self.exp_min >dataParamaters.min_expE:
            self.exp_min -= 1
            change_data = True
            ind_of_exp = -ind_of_exp

      if (change_data == True):
        X, Labels = dl.getAllTrainData(self.exp_min, self.exp_max)
        print("Got all data")
        print("Memory required after getting data: " + str(getrusage(RUSAGE_SELF).ru_maxrss))
        self.X = tf.convert_to_tensor(X, dtype=tf.float32)
        print("Energies shape")
        print(self.X.shape)
        print("Converted energies to tensor")
        print("Memory required after tensor transformation: " + str(getrusage(RUSAGE_SELF).ru_maxrss))
        self.Labels = tf.convert_to_tensor(Labels, dtype=tf.float32)
        print("Converted labels to tensor")
        print("Labels shape")
        print(self.Labels.shape)
        remained_epoch = tf.constant(trainingInputs.max_epochs - epoch, dtype=tf.int64)
        dur_getTrainData_ultimate_start = time.time()
        self.getTrainData_ultimate(remained_epoch)
        dur_getTrainData_ultimate_stop = time.time()
        dur_getTrainData_ultimate += (dur_getTrainData_ultimate_stop - dur_getTrainData_ultimate_start)
        print ("Using "+ str(self.X.shape[0])+ " events")
        print ("Epoch: " + str(epoch))
        print ("Loading new data using indexes from " + str(self.exp_min) + " to " + str(self.exp_max))

      dur_convert_start = time.time()
      X, Labels = self.ds_iter.get_next()
      X_trains    = tf.reshape(X, self.X_batch_shape)
      cond_labels = tf.reshape(Labels, self.Labels_batch_shape)   
      dur_convert_stop = time.time()
      dur_convert += (dur_convert_stop - dur_convert_start)

      train_loop_start = time.time()
      D_loss_curr, G_loss_curr = self.train_loop(X_trains, cond_labels)
      train_loop_stop = time.time()

      dur_train_loop += (train_loop_stop - train_loop_start)

      G_loss_iter.append(G_loss_curr.numpy())
      D_loss_iter.append(-D_loss_curr.numpy())

      Epochs.append(epoch)

      if epoch == 0: 
        print("Model and loss values will be saved every " + str(trainingInputs.sample_interval) + " epochs, the loss will also be plotted." )
      
      if epoch % trainingInputs.sample_interval == 0 and epoch > 0:

        try:
          self.saver.save(file_prefix = checkpoint_dir+ '/model')
        except:
          print("Something went wrong in saving iteration %s, moving to next one" % (epoch))
          print("exception message ", sys.exc_info()[0])     
        
        e_time = time.time()
        time_diff = e_time - s_time
        s_time = e_time
        memory = getrusage(RUSAGE_SELF).ru_maxrss

        time_iter.append(time_diff / trainingInputs.sample_interval)
        mem_iter.append(memory)
        
        print('Iter: {}; D loss: {:.4}; G_loss: {:.4}; TotalTime: {:.4}; DataPrep: {:.4}, Convert1: {:.4}, TrainLoop: {:.4}; Mem: {}'
            .format(epoch, D_loss_curr, G_loss_curr, time_diff, dur_getTrainData_ultimate, dur_convert, dur_train_loop, memory))
        dur_train_loop = dur_getTrainData_ultimate = dur_convert = 0.
            
    self.G_losses = G_loss_iter
    self.D_losses = D_loss_iter
    self.Epochs = Epochs

    np.savetxt(checkpoint_dir + "/d_loss.txt", D_loss_iter)
    np.savetxt(checkpoint_dir + "/g_loss.txt", G_loss_iter)
    np.savetxt(checkpoint_dir + "/time_per_epoch.txt", time_iter)
    np.savetxt(checkpoint_dir + "/memory.txt", mem_iter)

    self.plot_loss(trainingInputs)
    return

  def plot_loss(self, trainingInputs):
    import matplotlib.pyplot as plt
    loss_dir = trainingInputs.GAN_dir +'/%s/G_D_loss_iter_eta_%s_%s/' % (self.voxInputs.particle,self.voxInputs.eta_min,self.voxInputs.eta_max)
    if not os.path.exists(loss_dir): 
      os.makedirs(loss_dir)
    ax = plt.gca()
    ax.set_xlim(0, 1.1*self.Epochs[-1])
    ax.set_ylim(-1, 1)
    ax.cla()
    ax.plot(self.Epochs, self.G_losses, label="Generator")
    ax.plot(self.Epochs, self.D_losses, label="Discriminator")
    ax.set_xlabel('Epoch', fontsize=15)
    ax.set_ylabel('Wasserstein Loss', fontsize=15)
    ax.grid(True)
    ax.legend(fontsize=20)
    plt.savefig(loss_dir + 'loss.pdf')

  def load(self, epoch, labels, nevents, input_dir_gan):
    print("input_dir_gan = {}".format(input_dir_gan))
    model_name = "%s/model-%s" % (input_dir_gan, int(epoch/1000))
    print("Model name = {}".format(model_name))
    self.saver.restore(model_name)
    z = tf.random.normal([nevents, self.ganParameters.latent_dim], mean=0.5, stddev=0.5, dtype=tf.dtypes.float32)
    x_fake = self.G(inputs=[z, labels])
    return x_fake

  def GenerateEventsFromBest(self, checkpointfile, labels, nevents):
    self.saver.restore(checkpointfile) 
    z = tf.random.normal([nevents, self.ganParameters.latent_dim], mean=0.5, stddev=0.5, dtype=tf.dtypes.float32)
    x_fake = self.G(inputs=[z, labels])
    return x_fake
  
  def SaveModelForLWTNN(self, checkpointfile, output_dir): 
    print("Saving model from %s in %s" % (checkpointfile, output_dir))
    self.saver.restore(checkpointfile)
    
    self.G.save_weights(output_dir + '/checkpoint_%s_eta_%s_%s_%s.h5' % (self.voxInputs.particle, self.voxInputs.eta_min, self.voxInputs.eta_max, self.ganParameters.energy_range))
    generator_model_json = self.G.to_json()
    with open(output_dir + "/generator_model_%s_eta_%s_%s_%s.json" % (self.voxInputs.particle, self.voxInputs.eta_min, self.voxInputs.eta_max, self.ganParameters.energy_range), "w") as json_file:
      json_file.write(generator_model_json)    

  def GetGenerator(self): 
    return self.G

