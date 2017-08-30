#
# 	Behavioral Cloning Project 
# 	July 2017 
#	Author Nicholas Johnson 
#	Software uses Keras to create a Machine Learning Pipesample
#	The Output will be a stearing angel based on training data
#	Goal to Drive a Car around a simulated track 
#

import csv
import cv2 
import numpy as np
import os
import h5py
import sklearn
from sklearn.utils import shuffle
np.random.seed(0)


def generator(samples, batch_size):
	#    Generator to process a certain portion of the model at a time
	#    :param data_dir: The data directory
	#    :param image_paths: The paths to the images
	#    :param steer_angles: The steering angles
	#    :param batch_size: The batch size
	#    :param is_training: Whether this is training data (True) or validation data (False)
	num_samples = len(samples)
	while 1: # Loop forever so the generator never terminates
		shuffle(samples)
		for offset in range(0, num_samples, batch_size):
			batch_samples = samples[offset:offset+batch_size]

			images = []
			measurements = []
			for batch_sample in batch_samples:
				for i in range(3):
					source_path = sample[i]
					name = source_path.split('/')[-1]
					current_path = '../data7/IMG/' + name
					image = cv2.imread(current_path)
					images.append(image)
				correction = 0.05 
				# Number was chosen with trail and error, I tried 1 and found the car was jerky.
				# I saw David use 0.02 and felt it was too week at times, so I selected 0.05. 
				measurement = float(sample[3])
				measurements.append(measurement)
				measurements.append(measurement+correction)
				measurements.append(measurement-correction)

			# import Images 
			augmented_images = []
			augmented_measurements = []
			for image, measurement in zip(images, measurements):
				augmented_images.append(image)
				augmented_measurements.append(measurement)
				flipped_image = cv2.flip(image, 1)
				flipped_measurement = float(measurement) * -1.0
				augmented_images.append(flipped_image)
				augmented_measurements.append(flipped_measurement)
				augmented_measurements.append(flipped_measurement+correction)
				augmented_measurements.append(flipped_measurement-correction)

		# trim image to only see section with road 
		X_data = np.array(augmented_images)
		y_data = np.array(augmented_measurements)
		print("X_train ", X_data.shape)
		print("y_train ", y_data.shape)
		yield sklearn.utils.shuffle(X_data, y_data)

# plot function to be called after running the model
def plot_results(history, num = 0):
    #Plot the results 
    #:param history: The fit model
    #:param num: The number for the output file to save to
    # Plot training and validation loss
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model mean squared error loss')
    plt.ylabel('mean squared error loss')
    plt.xlabel('epoch')
    plt.legend(['training set', 'validation set'], loc='upper right')
    plt.savefig('training_validation_loss_plot_' + str(num) + '.jpg')
    plt.show()
    plt.close()

# import data 
samples = []
with open('../data7/driving_log.csv') as csvfile:
        reader = csv.reader(csvfile)
        for sample in reader:
                samples.append(sample)

# split Data into Traning and Validation 
test_size = 0.2
random_state = 0
# compile and train the model using the generator function
from sklearn.model_selection import train_test_split
#train_samples, validation_samples = train_test_split(samples,  test_size=test_size, random_state=random_state)
#train_generator = generator(train_samples, batch_size=32)
#validation_generator = generator(validation_samples, batch_size=32)

#print('train_generator:', train_generator.shape)
#print('validation_generator:', validation_generator.shape)
#Make lines a numpy array

# from sklearn.model_selection import train_test_split
X_train, X_valid, y_train, y_valid = train_test_split(samples, test_size=test_size, random_state=random_state)
X_train_generator = generator(X_train, batch_size=32)
X_validation_generator = generator(X_valid, batch_size=32)
Y_train_generator = generator(y_train, batch_size=32)
Y_validation_generator = generator(y_valid, batch_size=32)


print('X_train shape', X_train.shape)
print('Y_train shape', y_train.shape)
print('X_valid shape', X_valid.shape)
print('y_valid shape', y_valid.shape)

from keras.models import Sequential
from keras.layers import Flatten, Dense, Lambda, Dropout, Cropping2D
from keras.layers.convolutional import Convolution2D
from keras.layers.pooling import MaxPooling2D
from keras.optimizers import adam
from keras.callbacks import ModelCheckpoint

# model peramiters 
keep_prob = 0.5
video_H = 160
viedo_L = 320
layers = 3
crop_H = 25
crop_W = 70


model = Sequential()
# model.add(Lambda(lambda x: x / 255.0 - 0.5, input_shape=(video_H, viedo_L, layers)))
# Preprocess incoming data, centered around zero with small standard deviation 
model.add(Lambda(lambda x: x / 255.0 - 1., input_shape=(video_H, viedo_L, layers), output_shape=(video_H, viedo_L, layers)))
model.add(Cropping2D(cropping=((crop_W, crop_H), (0,0))))
model.add(Convolution2D(24,5,5, subsample=(2,2), activation="relu"))
model.add(Convolution2D(36,5,5, subsample=(2,2), activation="relu"))
model.add(Convolution2D(48,5,5, subsample=(2,2), activation="relu"))
model.add(Convolution2D(64,3,3, activation="relu"))
model.add(Convolution2D(64,3,3, activation="relu"))
model.add(Dropout(keep_prob))
model.add(Flatten())
model.add(Dense(100, activation="relu"))
model.add(Dense(50, activation="relu"))
model.add(Dense(10, activation="relu"))
model.add(Dense(1))
model.summary()


#Create a checkpoint of the model 
checkpoint = ModelCheckpoint('model-{epoch:03d}.h0',
                             monitor='val_loss',
                             verbose=0,
                             save_best_only=True,
                             mode='auto')

# set constant numbers for model generation
samples_per_epoch = 40
num_epochs = 10
learn_rate = 0.0001

# create a model and save it
model.compile(loss='mse', optimizer=adam(lr=learn_rate))
#model.fit(images, steering, validation_split=0.2, shuffle=True, nb_epoch=epoch) - Used for Orginal training 
### 

history_object = model.fit_generator(X_train_generator, Y_train_generator, \
	shuffle=True 
 	samples_per_epoch=len(X_train_samples), \
 	validation_data=X_validation_generator, \
 	nb_val_samples=len(X_validation_samples), \
	callbacks=[checkpoint],
 	nb_epoch=num_epochs,
 	verbose=1)

# history_object = model.fit_generator(generator(X_train, y_train, samples_per_epoch, True),
#                     samples_per_epoch,
#                     num_epochs,
#                     max_q_size=1,
#                     validation_data=generator(img_path, train_generator, train_generator, samples_per_epoch, False),
#                     nb_val_samples=len(X_valid),
#                     callbacks=[checkpoint],
#                     verbose=1)

model.save('nvidia05.h5')
plot_results(history_object, 0)
exit()
