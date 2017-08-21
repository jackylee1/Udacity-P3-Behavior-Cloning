import csv
import cv2
import numpy as np

lines = []
with open('../data2/driving_log.csv') as csvfile:
	reader = csv.reader(csvfile)
	for line in reader:
		lines.append(line)

images = []
measurements = []
for line in lines:
	for i in range(3):	
		source_path = line[i]
		filename = source_path.split('/')[-1]
		current_path = '../data2/IMG/' + filename
		image = cv2.imread(current_path)
		images.append(image)
	correction = 0.05
	measurement = float(line[3])
	measurements.append(measurement)
	measurements.append(measurement+correction)
	measurements.append(measurement-correction)		


augmented_images = []
augmented_measurements = []
for image, measurement in zip(images, measurements):
	augmented_images.append(image)
	augmented_measurements.append(measurement)
	flipped_image = cv2.flip(image, 1)
	flipped_measurement = float(measurement) * -1.0 
	augmented_images.append(flipped_image)
	augmented_measurements.append(flipped_measurement)

X_train = np.array(images)
y_train = np.array(measurements)

print('X_train shape:', X_train.shape)
print('y_train shape:', y_train.shape)

from keras.models import Sequential
from keras.layers import Flatten, Dense, Lambda, Cropping2D
from keras.layers.convolutional import Convolution2D
from keras.layers.pooling import MaxPooling2D 

model = Sequential()
model.add(Lambda(lambda x: x / 255.0 - 0.5, input_shape=(160,320,3)))
model.add(Cropping2D(cropping=((70,25), (0,0))))
model.add(Convolution2D(24,5,5, subsample=(2,2), activation="relu"))
model.add(Convolution2D(36,5,5, subsample=(2,2), activation="relu"))
model.add(Convolution2D(48,5,5, subsample=(2,2), activation="relu"))
model.add(Convolution2D(64,3,3, activation="relu"))
model.add(Convolution2D(64,3,3, activation="relu"))
model.add(Flatten())
model.add(Dense(128))
model.add(Dense(64))
model.add(Dense(1))

model.compile(loss='mse', optimizer='adam')
model.fit(X_train, y_train, validation_split=0.2, shuffle=True, nb_epoch=5)

model.save('nvidia.h5')
exit()
