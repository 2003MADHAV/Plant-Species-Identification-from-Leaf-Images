import streamlit as st
import numpy as np
import tensorflow as tf
from keras.preprocessing import image
import keras
import matplotlib.pyplot as plt
from PIL import Image
import os
import cv2
import skimage.exposure

# Updated list of plant species labels
labels = ["Ulmus carpinifolia","Acer","Salix aurita","Quercus","Alnus incana","Betula pubescens","Salix alba 'Sericea", "Populus tremula","Ulmus glabra","Sorbus aucuparia","Salix sinerea","Populus","Tilia","Sorbus intermedia","Fagus silvatica"]

# Function to predict the species of the plant based on the trained model and input image
def prediction(img_path, model):
    # Load and preprocess the image
    img = image.load_img(img_path, target_size=(224, 224), grayscale=True)  # Resize the image to (224, 224)
    img = image.img_to_array(img)
    img = img.reshape(-1, 224, 224, 1)
    img = img.astype('float32')
    img = img / 255.0

    # Predict the class
    lst = model.predict(img)
    index = np.argmax(lst, axis=-1)[0]
    return index, lst[0][index]


# Applying a mask to images with a noisy background image helps in more accurate classification
# This mask filters out all the green elements from the image, keeping in mind leaves are usually green
def apply_mask(img_path):
	img = cv2.imread(img_path)
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	range1 = (36, 0, 0)
	range2 = (86, 255, 255)
	mask = cv2.inRange(hsv, range1, range2)
	result = img.copy()
	result[mask == 0] = (255, 255, 255)
	cv2.imwrite("result.jpg", result)
	return result

# Focuses mainly on the UI designs from here and calling the required functions when necessary 
def main():
	image_file = st.file_uploader("Drag and drop file here\nLimit 200MB per file")

	if (st.button("Predict")):
		if image_file is not None:
			c1, c2 = st.columns([1, 5])
			with c1:
				img = Image.open(image_file)
				st.image(img, caption="Uploaded Image", width=100)
			with c2:
				with open(image_file.name, "wb") as f:
					f.write(image_file.getbuffer())
				st.write("Classifying...")
				result = ""
				model = keras.models.load_model(r"C:\Users\ASUS\project\Plant-Leaf-Recognition\CNN-model.h5")
				result, acc = prediction(image_file.name, model)
				if (acc < 0.5):
					st.success("Low accuracy warning! Let us try using a customized mask.")
					img2 = apply_mask(image_file.name)
					with c1:
						st.image(img2, caption="Masked Image", width=100)
					result, acc = prediction("result.jpg", model)
					st.success("This leaf is from the species: {} => Accuracy: {}%".format(labels[result], round(acc * 100, 2)))
				else:
					st.success("This leaf is from the species: {} => Accuracy: {}%".format(labels[result], round(acc * 100, 2)))
				# Adds a google search link to the predicted species for a better user experience 
				search_fields = labels[result].split()
				search = ""
				for tag in search_fields:
					search += tag + "+"
				st.write("[Click here to learn more about these species!](https://www.google.com/search?q={}leaf)".format(search))
		else:
			st.write("Please upload an image.")

if __name__ == '__main__':
	main()
