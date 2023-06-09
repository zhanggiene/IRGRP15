

LEARNINGRATE=0.01
import tensorflow as tf
import re
from transformers import *
import numpy as np
def decontraction(sentence):
	# Specific
	sentence = re.sub(r"won\'t", "will not", sentence)
	sentence = re.sub(r"can\'t", "can not", sentence)

	# General
	sentence = re.sub(r"n\'t", " not", sentence)
	sentence = re.sub(r"\'re", " are", sentence)
	sentence = re.sub(r"\'s", " is", sentence)
	sentence = re.sub(r"\'d", " would", sentence)
	sentence = re.sub(r"\'ll", " will", sentence)
	sentence = re.sub(r"\'t", " not", sentence)
	sentence = re.sub(r"\'ve", " have", sentence)
	sentence = re.sub(r"\'m", " am", sentence)
	return sentence

def preprocess_sentence(review):
	# Remove website links
	review = re.sub(r"http\S+", "", review)
	# Remove html tags
	review = re.sub(r"<.*?>", "", review)
	# Remove contraction
	review = decontraction(review)
	# Remove non-alphabet in sentence
	review = re.sub("[^A-Za-z]+", " ", review)
	# Convert to lower case
	review = " ".join(word.lower() for word in review.split())

	return review.strip()


				   
def predict_internal(model, review,tokenizer):
    review = preprocess_sentence(review)
    tokenized_review = tokenizer.encode(review, truncation=True, padding=True, return_tensors="tf")
    prediction = model.predict(tokenized_review, verbose=0)[0]
    output = tf.argmax(tf.nn.softmax(prediction, axis=1), axis=1)[0]
    if output == 0:
        return "grey" # Do grey colour on the review # nueral 
    elif output == 1:
        return "red" # Do red colour on the review  # negative 
    elif output == 2:
        return "green" # Do green colour on the review # positive





def predict(sentence):
    tokernizer = BertTokenizer.from_pretrained("bert-base-uncased")
    checkpoint = "checkpoint_bert_sentiment_bal_data_expand/variables/variables"
    bert_model =  TFBertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=3)
    bert_model.load_weights(checkpoint).expect_partial()
    bert_model.compile(optimizer=tf.keras.optimizers.legacy.Adam(learning_rate=0.00002), 
				   loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), 
				   metrics=[tf.keras.metrics.SparseCategoricalAccuracy("accuracy")])
    return predict_internal(bert_model,sentence,tokernizer)