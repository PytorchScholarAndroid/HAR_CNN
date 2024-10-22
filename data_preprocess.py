# encoding=utf-8
"""
    Created on 10:38 2018/11/10 
    @author: Jindong Wang
    
    Modified on 23:34 2018/12/25
    @contributor: Matheus Jacques
    add: create_validation_set(train_data, test_data, batch_size)
    modify: load(batch_size=64)
"""

# Imports

import numpy as np
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.sampler import SubsetRandomSampler
from torchvision import transforms


# This is for parsing the X data, you can ignore it if you do not need preprocessing
def format_data_x(datafile):
    x_data = None
    for item in datafile:
        item_data = np.loadtxt(item, dtype=np.float)
        if x_data is None:
            x_data = np.zeros((len(item_data), 1))
        x_data = np.hstack((x_data, item_data))
    x_data = x_data[:, 1:]
    print(x_data.shape)
    X = None
    for i in range(len(x_data)):
        row = np.asarray(x_data[i, :])
        row = row.reshape(9, 128).T
        if X is None:
            X = np.zeros((len(x_data), 128, 9))
        X[i] = row
    print(X.shape)
    return X


# This is for parsing the Y data, you can ignore it if you do not need preprocessing
def format_data_y(datafile):
    data = np.loadtxt(datafile, dtype=np.int) - 1
    YY = np.eye(6)[data]
    return YY


# Load data function, if there exists parsed data file, then use it
# If not, parse the original dataset from scratch
def load_data():
    import os
    if os.path.isfile('data/data_har.npz') == True:
        data = np.load('data/data_har.npz')
        X_train = data['X_train']
        Y_train = data['Y_train']
        X_test = data['X_test']
        Y_test = data['Y_test']
    else:
        # This for processing the dataset from scratch
        # After downloading the dataset, put it to somewhere that str_folder can find
        str_folder = '/home/jacquesmats/Documents/projects/HAR_CNN/' + 'UCI HAR Dataset/'
        INPUT_SIGNAL_TYPES = [
            "body_acc_x_",
            "body_acc_y_",
            "body_acc_z_",
            "body_gyro_x_",
            "body_gyro_y_",
            "body_gyro_z_",
            "total_acc_x_",
            "total_acc_y_",
            "total_acc_z_"
        ]

        str_train_files = [str_folder + 'train/' + 'Inertial Signals/' + item + 'train.txt' for item in
                           INPUT_SIGNAL_TYPES]
        str_test_files = [str_folder + 'test/' + 'Inertial Signals/' + item + 'test.txt' for item in INPUT_SIGNAL_TYPES]
        str_train_y = str_folder + 'train/y_train.txt'
        str_test_y = str_folder + 'test/y_test.txt'

        X_train = format_data_x(str_train_files)
        X_test = format_data_x(str_test_files)
        Y_train = format_data_y(str_train_y)
        Y_test = format_data_y(str_test_y)

    return X_train, onehot_to_label(Y_train), X_test, onehot_to_label(Y_test)


def onehot_to_label(y_onehot):
    a = np.argwhere(y_onehot == 1)
    return a[:, -1]


class data_loader(Dataset):
    def __init__(self, samples, labels, t):
        self.samples = samples
        self.labels = labels
        self.T = t

    def __getitem__(self, index):
        sample, target = self.samples[index], self.labels[index]
        return self.T(sample), target

    def __len__(self):
        return len(self.samples)
    
def create_validation_set(train_data, test_data,batch_size):
    # obtain training indices that will be used for validation
    num_train = len(train_data)
    indices = list(range(num_train))
    np.random.shuffle(indices)
    split = int(np.floor(0.2 * num_train)) # Validation Dataset set to 20%
    train_idx, valid_idx = indices[split:], indices[:split]

    # define samplers for obtaining training and validation batches
    train_sampler = SubsetRandomSampler(train_idx)
    valid_sampler = SubsetRandomSampler(valid_idx)

    # prepare data loaders (combine dataset and sampler)
    train_loader = DataLoader(train_data, batch_size=batch_size,
        sampler=train_sampler)
    valid_loader = DataLoader(train_data, batch_size=batch_size, 
        sampler=valid_sampler)
    test_loader = DataLoader(test_data, batch_size=batch_size)
    
    return train_loader, valid_loader, test_loader


def load(batch_size=64):
    x_train, y_train, x_test, y_test = load_data()
    x_train, x_test = x_train.reshape((-1, 9, 1, 128)), x_test.reshape((-1, 9, 1, 128))
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=(0,0,0,0,0,0,0,0,0), std=(1,1,1,1,1,1,1,1,1))
    ])
    
    train_set = data_loader(x_train, y_train, transform)
    test_set = data_loader(x_test, y_test, transform)
    
    train_loader, valid_loader, test_loader = create_validation_set(train_set, test_set,batch_size)
    
    return train_loader, valid_loader, test_loader
