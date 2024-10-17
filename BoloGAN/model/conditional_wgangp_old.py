import numpy as np
#import matplotlib.pyplot as plt
#import matplotlib as mpl

import os, sys
import time
import math
from sklearn.utils import shuffle
from cycler import cycler
from resource import *

import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()

from InputParameters import InputParameters
from TrainingInputParameters import TrainingInputParameters
from SetOptionsFromPath import SetOptionsFromPath
from DataReader import DataLoader
from XMLHandler import XMLHandler

#mpl.rcParams['axes.prop_cycle'] = cycler(color=['b', 'r', 'k'])
#mpl.rcParams['lines.linewidth'] = 2.0
#mpl.use('Agg')


class WGANGP():
  def __init__(self, inputs, output_dir_gan):
    self.inputs = inputs
    
    optimised = SetOptionsFromPath.GetGANArchitecture(output_dir_gan)
    if (optimised):
      ## optimised
      self.batchsize = 1024
      self.lam = 3
      self.n_disc = 8
      self.lr = 5e-5
    else:
      ## Original values
      self.batchsize = 128
      self.lam = 10
      self.n_disc = 5
      self.lr = 1e-4

    self.conditional_dim = 3
    
    largeLatentSpace = False
    if (largeLatentSpace):
      self.latent_dim = 100
      self.generatorLayers = [100,150,200]
    else:
      self.latent_dim = 50
      self.generatorLayers = [50,100,200]

    self.exp_min = 0 
    self.exp_max = 0
    self.batchIter = 0   
    self.useWeights = False
          
    self.xml = XMLHandler(self.inputs)
    self.img_dim = self.xml.GetTotalNumberOfBins()
    self.energy_dim = self.xml.GetTotalNumberOfEnergyBins()
        
    print("Initialised GAN with HP")
    print("  * batch size       : " + str(self.batchsize))
    print("  * Lambda           : " + str(self.lam))
    print("  * Training d/g     : " + str(self.n_disc))
    print("  * Learning rate    : " + str(self.lr))
    print("  * Latent space     : " + str(self.latent_dim))
    print("  * Generator layers : " + str(self.generatorLayers[0]) + ", " + str(self.generatorLayers[1]) + ", "+ str(self.generatorLayers[2]))
    print("  * Image size       : " + str(self.img_dim))
    print("  * Energy size      : " + str(self.energy_dim))
    

    #GAN structure must be defined after dimension is taken from XML
    self.E_dim = []
    self.x = tf.placeholder(tf.float32, shape=[None, self.img_dim])
    self.x_energy = tf.placeholder(tf.float32, shape=[None, self.img_dim])
    self.x_extrapWeights = tf.placeholder(tf.float32, shape=[None, self.img_dim])

    self.D_W1 = tf.Variable(self.xavier_init([self.img_dim + self.conditional_dim, self.img_dim]))
    self.D_b1 = tf.Variable(tf.zeros(shape=[self.img_dim]))

    self.D_W2 = tf.Variable(self.xavier_init([self.img_dim , self.img_dim]))
    self.D_b2 = tf.Variable(tf.zeros(shape=[self.img_dim]))

    self.D_W3 = tf.Variable(self.xavier_init([self.img_dim, self.img_dim]))
    self.D_b3 = tf.Variable(tf.zeros(shape=[self.img_dim]))

    self.D_W4 = tf.Variable(self.xavier_init([self.img_dim, 1]))
    self.D_b4 = tf.Variable(tf.zeros(shape=[1]))

    theta_D = [self.D_W1, self.D_W2, self.D_W3, self.D_W4, self.D_b1, self.D_b2, self.D_b3, self.D_b4]

    self.z = tf.placeholder(tf.float32, shape=[None, self.latent_dim])
    self.y = tf.placeholder(tf.float32, shape=[None, self.conditional_dim])

    
    self.G_W1 = tf.Variable(self.xavier_init([self.latent_dim + self.conditional_dim, self.generatorLayers[0]]))
    self.G_b1 = tf.Variable(tf.zeros(shape=[self.generatorLayers[0]]))

    self.G_W2 = tf.Variable(self.xavier_init([self.generatorLayers[0], self.generatorLayers[1]])) 
    self.G_b2 = tf.Variable(tf.zeros(shape=[self.generatorLayers[1]]))

    self.G_W3 = tf.Variable(self.xavier_init([self.generatorLayers[1], self.generatorLayers[2]]))
    self.G_b3 = tf.Variable(tf.zeros(shape=[self.generatorLayers[2]]))

    self.G_W4 = tf.Variable(self.xavier_init([self.generatorLayers[2], self.img_dim]))
    self.G_b4 = tf.Variable(tf.zeros(shape=[self.img_dim]))

    theta_G = [self.G_W1, self.G_W2, self.G_W3, self.G_W4, self.G_b1, self.G_b2, self.G_b3, self.G_b4]
    
    self.G_sample = self.G(self.z)
    self.D_real = self.D(self.x)
    #self.D_real_energy = self.D(self.x_energy)
    #self.D_real_extrapWeights = self.D(self.x_extrapWeights)
    self.D_fake = self.D(self.G_sample)
     
    eps = tf.random_uniform([self.batchsize, 1], minval=0., maxval=1.)
    X_inter = eps * self.x + (1. - eps) * self.G_sample
    grad = tf.gradients(self.D(X_inter), [X_inter])[0]
    grad_norm = tf.sqrt(tf.reduce_sum(tf.square(grad), axis=1))
    grad_pen = self.lam * tf.reduce_mean((grad_norm - 1)**2)

    self.D_loss = tf.reduce_mean(self.D_fake) - tf.reduce_mean(self.D_real) + grad_pen
    #self.D_loss_split = tf.reduce_mean(self.D_fake) - tf.reduce_mean(self.D_real_energy) - 0.01*tf.reduce_mean(self.D_real_extrapWeights) + grad_pen
    self.G_loss = -tf.reduce_mean(self.D_fake)

    self.D_solver = (tf.train.AdamOptimizer(learning_rate=self.lr, beta1=0.5)
        .minimize(self.D_loss, var_list=theta_D))
    #self.D_solver_split = (tf.train.AdamOptimizer(learning_rate=self.lr, beta1=0.5)
    #    .minimize(self.D_loss_split, var_list=theta_D))
    self.G_solver = (tf.train.AdamOptimizer(learning_rate=self.lr, beta1=0.5)
        .minimize(self.G_loss, var_list=theta_G)) 

    self.saver = tf.train.Saver(max_to_keep = None)        

    self.sess = tf.Session()
    h_est = self.sess.run(tf.global_variables_initializer())
        
    
  def G(self,z):
      z = tf.concat([z, self.y], 1)
      G_h1 = tf.nn.relu(tf.matmul(z, self.G_W1) + self.G_b1)   
      #G_h1 = tf.concat([G_h1, self.y], 1)
      G_h2 = tf.nn.relu(tf.matmul(G_h1, self.G_W2) + self.G_b2)
      #G_h2 = tf.concat([G_h2, self.y], 1)
      G_h3 = tf.nn.relu(tf.matmul(G_h2, self.G_W3) + self.G_b3)
      #G_h3 = tf.concat([G_h3, self.y],1)
      G_o = tf.nn.relu(tf.matmul(G_h3, self.G_W4) + self.G_b4) 
      return G_o


  def D(self,x):
      x = tf.concat([x, self.y], 1)
      D_h1 = tf.nn.relu(tf.matmul(x, self.D_W1) + self.D_b1)
      #D_h1 = tf.concat([D_h1, self.y], 1)
      D_h2 = tf.nn.relu(tf.matmul(D_h1, self.D_W2) + self.D_b2)
      #D_h2 = tf.concat([D_h2, self.y], 1)
      D_h3 = tf.nn.relu(tf.matmul(D_h2, self.D_W3) + self.D_b3)
      #D_h3 = tf.concat([D_h3, self.y], 1)
      D_o = tf.matmul(D_h3, self.D_W4) + self.D_b4
      return D_o
  
  def getTrainData(self):
      numberOfEvents = len(self.X)
      numberOfBunches = int(numberOfEvents / self.batchsize)
              
      if (self.batchIter > numberOfBunches -1):
          self.batchIter = 0
      if (self.batchIter == 0):
          self.X_shuffled, self.label_shuffled = shuffle(self.X, self.Labels) 

      firstEvent = self.batchsize*self.batchIter
      lastEvent = self.batchsize*(self.batchIter+1) 
      
      self.batchIter=self.batchIter + 1

      return np.array(self.X_shuffled[firstEvent:lastEvent]), self.label_shuffled[firstEvent:lastEvent]
  
  def sample_z(self, m, n):
      return np.random.uniform(-1., 1., size=[m, n])	

  def xavier_init(self,size):
    in_dim = size[0]
    xavier_stddev = 1. / tf.sqrt(in_dim / 2.)
    return tf.random_normal(shape=size, stddev=xavier_stddev)


  def load(self, epoch, labels, nevents, input_dir_gan):
      init = tf.global_variables_initializer()
      with tf.Session() as sess:
          sess.run(init)   
          self.saver.restore(sess, input_dir_gan + "/%s/checkpoints_eta_%s_%s/model_%s.ckpt" % (self.inputs.particle,self.inputs.eta_min,self.inputs.eta_max,epoch))    
          samples = sess.run(self.G_sample, feed_dict={self.z: self.sample_z(nevents, self.latent_dim), self.y : labels})
                                
      return samples


  def train(self, trainingInputs):
      checkpoint_dir = trainingInputs.GAN_dir +'/%s/checkpoints_eta_%s_%s/' % (self.inputs.particle,self.inputs.eta_min,self.inputs.eta_max)
      loss_dir = trainingInputs.GAN_dir +'/%s/G_D_loss_iter_eta_%s_%s/' % (self.inputs.particle,self.inputs.eta_min,self.inputs.eta_max)

      if not os.path.exists(checkpoint_dir):
          os.makedirs(checkpoint_dir)
      if not os.path.exists(loss_dir): 
         os.makedirs(loss_dir)

      print ('training started')
      dl = DataLoader(self.inputs, trainingInputs, self.xml)
      #tf.reset_default_graph()          
      
      D_loss_iter = [] 
      G_loss_iter = []
  
      if trainingInputs.loadFromBaseline:
          try:
            region = self.xml.GetEtaRegion()
            print("Try to load best epoch from baseline folder %s" % (trainingInputs.loading_dir))
            self.saver.restore(self.sess, "%s/model_%s_eta_region_%s.ckpt" % (trainingInputs.loading_dir, self.inputs.particle,region))    
          except:
              print("Error while loading baseline checkpoint", sys.exc_info()[0])
              raise

      if trainingInputs.start_epoch > 0:          
          try:
            print("Try to load starting checkpoint %d" % (trainingInputs.start_epoch))
            self.saver.restore(self.sess, checkpoint_dir + "model_%s.ckpt" % (trainingInputs.start_epoch))    
            D_loss_iter = np.loadtxt(checkpoint_dir + "/d_loss.txt").tolist()
            G_loss_iter = np.loadtxt(checkpoint_dir + "/g_loss.txt").tolist()
            trainingInputs.start_epoch = trainingInputs.start_epoch + 1
            
          except:
              print("Error while loading checkpoint", sys.exc_info()[0])
              raise

      s_time = time.time()
      
      ind_of_exp = 1
      
      if (trainingInputs.training_strategy == "All"):
          print("Training is done using all sample together") 
          self.exp_max = trainingInputs.max_expE
          self.exp_min = trainingInputs.min_expE
      elif (trainingInputs.training_strategy == "Sequential"):
          print("Sequential training, first sample trained for " + str(trainingInputs.epochsForFirstSample) + " epochs, additional samples added at intervals of " + str(trainingInputs.epochsForAddingASample) + " epochs") 
          self.exp_max = trainingInputs.exp_mid
          self.exp_min = trainingInputs.exp_mid

      for epoch in range(0,trainingInputs.start_epoch): 
          #after 50000, each 20000 it makes larger the reange
          if trainingInputs.training_strategy == "Sequential" and epoch >= trainingInputs.epochsForFirstSample  and (epoch-trainingInputs.epochsForFirstSample) % trainingInputs.epochsForAddingASample == 0: 
             if ind_of_exp == 0 :
                self.exp_max += 1
                ind_of_exp += 1
             elif ind_of_exp > 0:
                if self.exp_max <trainingInputs.max_expE: 
                   self.exp_max += 1
                   ind_of_exp = -ind_of_exp
             else :
                if self.exp_min > trainingInputs.min_expE:
                   self.exp_min -= 1
                   ind_of_exp = -ind_of_exp
           
      for epoch in range(trainingInputs.start_epoch, trainingInputs.max_epochs): 
          change_data = False
          
          if epoch == trainingInputs.start_epoch:
            change_data = True
          
          if trainingInputs.training_strategy == "Sequential" and epoch >= trainingInputs.epochsForFirstSample  and (epoch-trainingInputs.epochsForFirstSample) % trainingInputs.epochsForAddingASample == 0: 
             #after 50000, each 20000 it makes larger the reange
             if ind_of_exp == 0 :
                self.exp_max += 1
                change_data = True
                ind_of_exp += 1
             elif ind_of_exp > 0:
                if self.exp_max <trainingInputs.max_expE: 
                   self.exp_max += 1
                   change_data = True
                   ind_of_exp = -ind_of_exp
             else :
                if self.exp_min >trainingInputs.min_expE:
                   self.exp_min -= 1
                   change_data = True
                   ind_of_exp = -ind_of_exp

          if epoch >= trainingInputs.epochsForWeights and not self.useWeights:
             change_data = True
             self.useWeights = True

          if (change_data == True):
             self.batchIter = 0
             print ("Epoch: " + str(epoch))
             print ("Loading new data using indexes from " + str(self.exp_min) + " to " + str(self.exp_max) + " using weights: " + str(self.useWeights))
             self.X, self.Labels  = dl.getAllTrainData(self.exp_min, self.exp_max,self.useWeights)              
             print ("Using "+ str(len(self.X))+ " events")
             #print (self.X[0])
             
          #memory_before_ndisc = getrusage(RUSAGE_SELF).ru_maxrss
          
          #mem1a = []
          #mem1b = []

          for _ in range(self.n_disc):
             #print(_)
             X_train, cond_label = self.getTrainData()                 
             #print(getrusage(RUSAGE_SELF).ru_maxrss)
             #mem1a.append(getrusage(RUSAGE_SELF).ru_maxrss)
             #self.E_dim = np.expand_dims(E_true, axis = 1)
             #print(cond_label)
             _, D_loss_curr = self.sess.run([self.D_solver, self.D_loss], feed_dict={self.x: X_train, self.z: self.sample_z(self.batchsize, self.latent_dim),self.y: cond_label})
             #_, D_loss_curr_split = self.sess.run([self.D_solver_split, self.D_loss_split], feed_dict={self.x_energy: X_train[:energy_dim], self.x_extrapWeights: X_train[energy_dim:], self.z: self.sample_z(self.batchsize, self.latent_dim),self.y: cond_label})
             #print(getrusage(RUSAGE_SELF).ru_maxrss)
             #mem1b.append(getrusage(RUSAGE_SELF).ru_maxrss)

          
          #memory_after_ndisc = getrusage(RUSAGE_SELF).ru_maxrss

          _, G_loss_curr = self.sess.run([self.G_solver, self.G_loss], feed_dict={self.z: self.sample_z(self.batchsize, self.latent_dim), self.y: cond_label})

          #memory_after_g_loss = getrusage(RUSAGE_SELF).ru_maxrss

          G_loss_iter.append(G_loss_curr)
          D_loss_iter.append(-D_loss_curr)
          #D_loss_split_iter.append(-D_loss_curr_split)

          #memory_after_loss_array = getrusage(RUSAGE_SELF).ru_maxrss
          
          #print('Iter: {}; Mem1: {}; Mem2: {}; Mem3: {}; Mem4: {}'
          #       .format(epoch, memory_before_ndisc, memory_after_ndisc, memory_after_g_loss, memory_after_loss_array))
          

          if epoch == 0: 
              print("Model and loss values will be saved every " + str(trainingInputs.sample_interval) + " epochs, the loss will also be plotted." )
          
          if epoch % trainingInputs.sample_interval == 0 and epoch > 0:
      
              self.saver.save(self.sess, checkpoint_dir + "/model_%s.ckpt" % (epoch))
              #clear session now!!!
              
              np.savetxt(checkpoint_dir + "/d_loss.txt", D_loss_iter)
              np.savetxt(checkpoint_dir + "/g_loss.txt", G_loss_iter)

              e_time = time.time()
              time_diff = e_time - s_time
              s_time = e_time
              memory = getrusage(RUSAGE_SELF).ru_maxrss
              
              print('Iter: {}; D loss: {:.4}; G_loss: {:.4}; Time: {}; Mem: {}'
                 .format(epoch, D_loss_curr, G_loss_curr, time_diff, memory))
              
              trainingInputs.total_time.append(time_diff)
              
              #h_D = TH1F("D_loss","D_loss:Epoch:Loss",epoch,0,epoch)
              #h_G = TH1F("G_loss","G_loss:Epoch:Loss",epoch,0,epoch)
              #for i in range(epoch):
              #  h_D.Fill(D_loss[i])
              #  h_G.Fill(G_loss[i])
              #  
              #canvas = ROOT.TCanvas('canvas_h', 'Total Energy comparison plots', 900, 900)
              #h_D.SetLineColor(ROOT.kRed)
              #h_G.SetLineColor(ROOT.kBlue)
              #h_D.GetYaxis().SetRangeUser(-1,1)
              #
              #h_D.Draw("HIST")
              #h_G.Draw("HIST same")
              #
              #leg = MakeLegend( lparams )
              #leg.SetTextFont( 42 )
              #leg.SetTextSize(0.1)
              #leg.AddEntry(h_D,"D loss","l") 
              #leg.Draw()
              #leg.AddEntry(h_G,"G loss","l")  
              #leg.Draw('same')
              ##legend = (particleName + ", " + str('{:.2f}'.format(int(eta_min)/100,2)) + "<|#eta|<" + str('{:.2f}'.format((int(eta_min)+5)/100,2)))
              ##ROOT.ATLAS_LABEL_BIG( 0.1, 0.9, ROOT.kBlack, legend )
              #
              #plotName_png="%s/G_D_loss_iter.png" % (loss_dir)
              #canvas.SaveAs(inputFile_Plot_png)
                           
              #fig = plt.figure(figsize=(20,10))
              #plt.axes()
              #ax11 = fig.add_subplot(111)
              #ax11.plot( G_loss_iter , label='G_loss')
              #ax11.plot( D_loss_iter , label='D_loss')
              #plt.ylim([-1,1])
              #ax11.set_xlabel('Iterations')
              #ax11.set_ylabel('Loss')
              #ax11.legend()
              #fig.savefig(loss_dir + "/G_D_loss_iter.png")
              #
              #plt.yscale('log')
              #fig.savefig(loss_dir + "/G_D_loss_iter_logy.png")
              #plt.close()
              
  
