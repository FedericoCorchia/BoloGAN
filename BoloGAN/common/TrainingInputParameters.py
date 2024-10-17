class TrainingInputParameters():
  def __init__(self, start_epoch, max_epochs, sample_interval, GAN_dir, training_strategy, epochsForFirstSample = 50000, epochsForAddingASample = 20000):
    self.start_epoch = int(start_epoch) 
    self.max_epochs = max_epochs 
    self.sample_interval = sample_interval 
    self.GAN_dir = GAN_dir
    self.training_strategy = training_strategy

    self.epochsForFirstSample = epochsForFirstSample 
    self.epochsForAddingASample = epochsForAddingASample
    self.loadFromBaseline = False

    self.Print()
            
  def Print(self):
    print ("Training inputs parameters")
    print (" Epochs from: " + str(self.start_epoch) + " to " + str(self.max_epochs) + " saving every " +  str(self.sample_interval))
    print ("")

class TrainingInputParametersFromSeed(TrainingInputParameters):
  def __init__(self, start_epoch, max_epochs, sample_interval, GAN_dir, training_strategy, loading_dir):
    super().__init__(start_epoch, max_epochs, sample_interval, GAN_dir, training_strategy)
    self.loading_dir = loading_dir 
    self.loadFromBaseline = True

    print(" Loading dir: "+self.loading_dir)

