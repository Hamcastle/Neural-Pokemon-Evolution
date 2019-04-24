from __future__ import print_function

from keras.models import Model
from keras.layers import Input, LSTM, Dense
import numpy as np
import pandas as pd
import os

def load_and_break_into_lines(path_to_data):
	try:
		with open(path_to_data,'r',encoding='utf-8') as f:
			lines = f.read().split('\n')
		return lines
	except:
		raise

def create_start_end_seqs(lines,num_samples=406):
	try:
		input_texts  = []
		target_texts = []
		input_characters  = set()
		target_characters = set()

		for line in lines[: min(num_samples, len(lines) - 1)]:
			input_text, target_text = line.split('\t')
			target_text = '\t' + target_text + '\n'
			input_texts.append(input_text)
			target_texts.append(target_text)
			
			for char in input_text:
				if char not in input_characters:
					input_characters.add(char)
			for char in target_text:
				if char not in target_characters:
					target_characters.add(char)

		return input_texts,target_texts,input_characters,target_characters
	except:
		raise

def generate_token_data(input_characters,target_characters,input_texts,target_texts):
	try:
		input_characters = sorted(list(input_characters))
		target_characters = sorted(list(target_characters))
		num_encoder_tokens = len(input_characters)
		num_decoder_tokens = len(target_characters)
		max_encoder_seq_length = max([len(txt) for txt in input_texts])
		max_decoder_seq_length = max([len(txt) for txt in target_texts])
		return input_characters,target_characters,num_encoder_tokens,num_decoder_tokens,max_encoder_seq_length,max_decoder_seq_length
	except:
		raise


def decode_sequence(input_seq):
    # Encode the input as state vectors.
    states_value = encoder_model.predict(input_seq)

    # Generate empty target sequence of length 1.
    target_seq = np.zeros((1, 1, num_decoder_tokens))
    # Populate the first character of target sequence with the start character.
    target_seq[0, 0, target_token_index['\t']] = 1.

    # Sampling loop for a batch of sequences
    # (to simplify, here we assume a batch of size 1).
    stop_condition = False
    decoded_sentence = ''
    while not stop_condition:
        output_tokens, h, c = decoder_model.predict(
            [target_seq] + states_value)

        # Sample a token
        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_char = reverse_target_char_index[sampled_token_index]
        decoded_sentence += sampled_char

        # Exit condition: either hit max length
        # or find stop character.
        if (sampled_char == '\n' or
           len(decoded_sentence) > max_decoder_seq_length):
            stop_condition = True

        # Update the target sequence (of length 1).
        target_seq = np.zeros((1, 1, num_decoder_tokens))
        target_seq[0, 0, sampled_token_index] = 1.

        # Update states
        states_value = [h, c]

    return decoded_sentence

def non_training_set_translation(input_string,max_encoder_seq_length=max_encoder_seq_length,num_encoder_tokens=num_encoder_tokens,input_token_index=input_token_index):
	try:
		input_string_tokenized = np.zeros((1,max_encoder_seq_length,num_encoder_tokens),dtype='float32')
		for t, char in enumerate(input_string):
			input_string_tokenized[0,t,input_token_index[char]] = 1.
		print((input_string,decode_sequence(input_string_tokenized)))
		return decode_sequence(input_string_tokenized).split('\n')[0]
	except:
		raise

def main():
	try:
		batch_size  = 75
		epochs      = 350
		latent_dim  = 128
		num_samples = 403
		names_data = 'pair_form_names.csv'

		lines = load_and_break_into_lines(names_data)
		input_texts,target_texts,input_characters,target_characters = create_start_end_seqs(lines,num_samples)
		input_characters,target_characters,num_encoder_tokens,num_decoder_tokens,max_encoder_seq_length,max_decoder_seq_length = generate_token_data(
			input_characters,target_characters,input_texts,target_texts)
		
		input_token_index = dict(
			[(char, i) for i, char in enumerate(input_characters)])
		target_token_index = dict(
			[(char, i) for i, char in enumerate(target_characters)])

		encoder_input_data = np.zeros(
			(len(input_texts), max_encoder_seq_length, num_encoder_tokens),
			dtype='float32')
		decoder_input_data = np.zeros(
			(len(input_texts), max_decoder_seq_length, num_decoder_tokens),
			dtype='float32')
		decoder_target_data = np.zeros(
			(len(input_texts), max_decoder_seq_length, num_decoder_tokens),
			dtype='float32')

		for i, (input_text, target_text) in enumerate(zip(input_texts, target_texts)):
			for t, char in enumerate(input_text):
				encoder_input_data[i, t, input_token_index[char]] = 1.
			for t, char in enumerate(target_text):
				decoder_input_data[i, t, target_token_index[char]] = 1.
				if t > 0:
					decoder_target_data[i, t - 1, target_token_index[char]] = 1.


		encoder_inputs = Input(shape=(None, num_encoder_tokens))
		encoder = LSTM(latent_dim, return_state=True)
		encoder_outputs, state_h, state_c = encoder(encoder_inputs)
		encoder_states = [state_h, state_c]

		decoder_inputs = Input(shape=(None, num_decoder_tokens))
		decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True)
		decoder_outputs, _, _ = decoder_lstm(decoder_inputs,
                                     initial_state=encoder_states)
		decoder_dense = Dense(num_decoder_tokens, activation='softmax')
		decoder_outputs = decoder_dense(decoder_outputs)
		model = Model([encoder_inputs, decoder_inputs], decoder_outputs)

		model.compile(optimizer='rmsprop', loss='categorical_crossentropy')
		model.fit([encoder_input_data, decoder_input_data], decoder_target_data,
			batch_size=batch_size,epochs=epochs,validation_split=0.2)

		encoder_model = Model(encoder_inputs, encoder_states)

		decoder_state_input_h = Input(shape=(latent_dim,))
		decoder_state_input_c = Input(shape=(latent_dim,))
		decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]
		decoder_outputs, state_h, state_c = decoder_lstm(
		    decoder_inputs, initial_state=decoder_states_inputs)
		decoder_states = [state_h, state_c]
		decoder_outputs = decoder_dense(decoder_outputs)
		decoder_model = Model(
		    [decoder_inputs] + decoder_states_inputs,
		    [decoder_outputs] + decoder_states)

		# Reverse-lookup token index to decode sequences back to
		# something readable.
		reverse_input_char_index = dict(
		    (i, char) for char, i in input_token_index.items())
		reverse_target_char_index = dict(
		    (i, char) for char, i in target_token_index.items())

		sword_and_shield_starters = ['Sobble','Scorbunny','Grookey']
		sword_and_shield_seconds  = [non_training_set_translation(each_name) for each_name in sword_and_shield_starters]
		sword_and_shield_thirds   = [non_training_set_translation(each_name) for each_name in sword_and_shield_seconds]


	except:
		raise