import argparse
import numpy as np
import json
import os
import time

from loader import Loader
from keras_models import model

np.random.seed(20)

NUMBER_EPOCHS = 200
VERBOSE_LEVEL = 1
FOLDER_TO_SAVE = "./saved/"


def get_folder_name(start_time, net_type):
    folder_name = FOLDER_TO_SAVE + net_type + '/' + start_time
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name


def get_filename_for_saving(start_time, net_type):
    saved_filename = get_folder_name(start_time, net_type) + \
        "/{epoch:002d}-{val_loss:.2f}.hdf5"
    return saved_filename


def plot_model(model, start_time, net_type):
    from keras.utils.visualize_util import plot
    plot(
        model,
        to_file=get_folder_name(start_time, net_type) + '/model.png',
        show_shapes=True,
        show_layer_names=False)


def save_params(params, start_time, net_type):
    saving_filename = get_folder_name(start_time, net_type) + "/params.json"
    with open(saving_filename, 'w') as outfile:
        json.dump(params, outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("data_path", help="path to files")
    parser.add_argument("--refresh", help="whether to refresh cache")
    args = parser.parse_args()
    net_type = 'conv'

    dl = Loader(
        args.data_path,
        use_one_hot_labels=True,
        use_cached_if_available=not args.refresh)

    x_train = dl.x_train[:, :, np.newaxis]
    y_train = dl.y_train
    print("Training size: " + str(len(x_train)) + " examples.")

    x_val = dl.x_test[:, :, np.newaxis]
    y_val = dl.y_test
    print("Validation size: " + str(len(x_val)) + " examples.")

    start_time = str(int(time.time()))
    params = {
        "subsample_lengths": [2, 2, 2, 5, 5],
        "filter_length": 32,
        "num_filters": 32,
        "dropout": 0.3,
        "recurrent_layers": 1,
        "recurrent_hidden": 64,
        "dense_layers": 1,
        "dense_hidden": 64,
        "version": 1
    }

    save_params(params, start_time, net_type)

    params.update({
        "input_shape": x_train[0].shape,
        "num_categories": dl.output_dim
    })

    network = model.build_network(**params)

    try:
        plot_model(network, start_time, net_type)
    except:
        print("Skipping plot")

    from keras.callbacks import ModelCheckpoint
    checkpointer = ModelCheckpoint(
        filepath=get_filename_for_saving(start_time, net_type),
        verbose=2,
        save_best_only=True)

    network.fit(
        x_train, y_train,
        validation_data=(x_val, y_val),
        nb_epoch=NUMBER_EPOCHS,
        callbacks=[checkpointer],
        verbose=VERBOSE_LEVEL)
