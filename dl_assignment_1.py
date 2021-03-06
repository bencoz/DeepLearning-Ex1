import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

np.random.seed(42)

"""The following class represents a simple feed forward network with multiple layers. The network class provides methods for running forward and backward for a single instance, throught the network. You should implement the methods (indicated with TODO), that performs forward and backward for an entire batch. Note, the idea is to use matrix multiplications, and not running standard loops over the instances in the batch."""


class MyNN:
    def __init__(self, learning_rate, layer_sizes):
        '''
        learning_rate - the learning to use in backward
        layer_sizes - a list of numbers, each number repreents the nuber of neurons
                      to have in every layer. Therfore, the length of the list
                      represents the number layers this network has.
        '''
        self.learning_rate = learning_rate
        self.layer_sizes = layer_sizes
        self.model_params = {}
        self.memory = {}
        self.grads = {}

        # Initializing weights
        for layer_index in range(len(layer_sizes) - 1):
            W_input = layer_sizes[layer_index + 1]
            W_output = layer_sizes[layer_index]
            self.model_params['W_' + str(layer_index + 1)] = np.random.randn(W_input, W_output) * 0.1
            self.model_params['b_' + str(layer_index + 1)] = np.random.randn(W_input) * 0.1

    def forward_single_instance(self, x):
        a_i_1 = x
        self.memory['a_0'] = x
        for layer_index in range(len(self.layer_sizes) - 1):
            W_i = self.model_params['W_' + str(layer_index + 1)]
            b_i = self.model_params['b_' + str(layer_index + 1)]
            z_i = np.dot(W_i, a_i_1) + b_i
            a_i = 1 / (1 + np.exp(-z_i))
            self.memory['a_' + str(layer_index + 1)] = a_i
            a_i_1 = a_i
        return a_i_1

    def log_loss(self, y_hat, y):
        '''
        Logistic loss, assuming a single value in y_hat and y.
        '''
        m = y_hat[0]
        cost = -y[0] * np.log(y_hat[0]) - (1 - y[0]) * np.log(1 - y_hat[0])
        return cost

    def backward_single_instance(self, y):
        a_output = self.memory['a_' + str(len(self.layer_sizes) - 1)]
        dz = a_output - y

        for layer_index in range(len(self.layer_sizes) - 1, 0, -1):
            a_l_1 = self.memory['a_' + str(layer_index - 1)]
            dW = np.dot(dz.reshape(-1, 1), a_l_1.reshape(1, -1))
            self.grads['dW_' + str(layer_index)] = dW
            W_l = self.model_params['W_' + str(layer_index)]
            db = dz.reshape(-1)

            self.grads[f'db_{str(layer_index)}'] = db
            dz = (a_l_1 * (1 - a_l_1)).reshape(-1, 1) * np.dot(W_l.T, dz.reshape(-1, 1))

    def update(self):
        for layer_index in range(len(self.layer_sizes) - 1):
            # updating W
            self.model_params['W_' + str(layer_index + 1)] = \
                self.model_params['W_' + str(layer_index + 1)] - \
                (self.grads['dW_' + str(layer_index + 1)] * self.learning_rate)

            # updating b
            self.model_params['b_' + str(layer_index + 1)] = \
                self.model_params['b_' + str(layer_index + 1)] - \
                (self.grads['db_' + str(layer_index + 1)] * self.learning_rate)

    def forward_batch(self, X):
        a_i_1 = X
        self.memory['A_0'] = X
        for layer_index in range(len(self.layer_sizes) - 1):
            W_i = self.model_params['W_' + str(layer_index + 1)]
            b_i = self.model_params['b_' + str(layer_index + 1)]
            z_i = np.dot(W_i, a_i_1) + b_i.reshape(-1, 1)
            a_i = 1 / (1 + np.exp(-z_i))
            self.memory['A_' + str(layer_index + 1)] = a_i
            a_i_1 = a_i
        return a_i_1

    def backward_batch(self, y):
        a_output = self.memory['A_' + str(len(self.layer_sizes) - 1)]
        dz = a_output - y

        for layer_index in range(len(self.layer_sizes) - 1, 0, -1):
            a_l_1 = self.memory['A_' + str(layer_index - 1)]

            dW = np.dot(dz, a_l_1.T) * (1 / y.shape[1])
            self.grads['dW_' + str(layer_index)] = dW
            W_l = self.model_params['W_' + str(layer_index)]

            db = dz.mean(axis=1)
            self.grads[f'db_{str(layer_index)}'] = db

            dz = (a_l_1 * (1 - a_l_1)) * np.dot(W_l.T, dz)

    def log_loss_batch(self, y_hat, y):
        cost = -y * np.log(y_hat) - (1 - y) * np.log(1 - y_hat)
        return cost.mean()


nn = MyNN(0.01, [3, 2, 1])

nn.model_params

x = np.random.randn(3)
y = np.random.randn(1)

y_hat = nn.forward_single_instance(x)
print(y_hat)

nn.backward_single_instance(y)


def train(X, y, epochs, batch_size):
    '''
  Train procedure, please note the TODOs inside
  '''
    epochs_loss_history = []
    for e in range(1, epochs + 1):
        epoch_loss = 0

        # shuffle
        indices = np.random.permutation(X.shape[1])
        X = X[:, indices]
        y = y[:, indices]

        # davide to batches
        batches = [(
            X[:, index * batch_size: (index + 1) * batch_size],
            y[:, index * batch_size: (index + 1) * batch_size])
            for index in range(int(X.shape[1] / batch_size) - 1)
        ]

        for X_b, y_b in batches:
            y_hat = nn.forward_batch(X_b)
            epoch_loss += nn.log_loss_batch(y_hat, y_b)
            nn.backward_batch(y_b)
            nn.update()

        epoch_loss = epoch_loss / len(batches)
        epochs_loss_history.append(epoch_loss)
        print(f'Epoch {e}, loss={epoch_loss}')
    return epochs_loss_history


# nn = MyNN(0.003, [6, 4, 3, 1])
#
# X = np.random.randn(6, 100)
# y = np.random.randn(1, 100)
# batch_size = 8
# epochs = 2
#
# loss_history = train(X, y, epochs, batch_size)
# plt.plot(loss_history)

"""#TODO: train on an external dataset

Train on the Bike Sharing dataset, using the same split as in *DL Notebook 4 - logistic regression*.
Use the following features from the data:

* temp
* atemp
* hum
* windspeed
* weekday

The response variable is, like in Notebook 4, raw["success"] = raw["cnt"] > (raw["cnt"].describe()["mean"]).

The architecture of the network should be: [5, 40, 30, 10, 7, 5, 3, 1].

Use batch_size=8, and train it for 100 epochs on the train set (based on the split as requested above).

Then, plot loss per epoch.
"""

# loading the data
raw = pd.read_csv('course-ml-data/Bike-Sharing-Dataset 2/day.csv')

X = (raw[['temp', 'atemp', 'hum', 'windspeed', 'weekday']]).values
y = raw["success"] = (raw["cnt"] > (raw["cnt"].describe()["mean"])).values
# print(y.reshape(1, -1).astype(int))

nn = MyNN(0.001, [5, 40, 30, 10, 7, 5, 3, 1])

epochs, batch_size = 100, 8

loss_history = train(X.T, y.reshape(1, -1).astype(int), epochs, batch_size)
plt.plot(loss_history)
plt.xlabel('Epoch')
plt.ylabel("Loss")
plt.title('Loss per Epoch')
plt.show()
