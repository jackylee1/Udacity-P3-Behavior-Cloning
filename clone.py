import csv
import cv2
import numpy as np

lines = []
with open('../data1/driving_log.csv') as csvfile:
	reader = csv.reader(csvfile)
	for line in reader:
		lines.append(line)

images = []
measurements =[]
for line in lines:
	for i in range(3):
		source_path = line[i]
		filename = source_path.split('/')[-1]
		current_path = '../data1/IMG/' + filename
		image = cv2.imread(current_path)
		images.append(image)
		measurement = float(line[3])
		measurements.append(measurement)

X_train = np.array(images)
y_train = np.array(measurements)

print('X_train shap:', X_train.shape)
print('y_train shap:', y_train.shape)

from keras.models import Sequential
from keras.layers import Flatten, Dense, Lambda

model = Sequential()
model.add(Lambda(lambda x: x / 255 - 0.5, input_shape=(160,320,3)))
model.add(Flatten())
model.add(Dense(1))

model.compile(loss='mse', optimizer='adam')
model.fit(X_train, y_train, validation_split=0.2, shuffle=True, nb_epoch=5)

model.save('model.h5')
exit()
