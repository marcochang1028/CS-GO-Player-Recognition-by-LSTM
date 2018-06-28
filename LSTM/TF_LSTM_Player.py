import glob
from os import listdir, path
import pandas as pd
import numpy as np
from sklearn import preprocessing
from datetime import datetime
from random import shuffle
import tensorflow as tf
import sys

def shuffle_in_unison(a, b):
    """Shuffle two arrays at the same time.
        
    Args:
        a -- first array
        b -- second array
    returns:
        a -- shuffled a
        b -- shuffled b
    """
    assert len(a) == len(b)
    shuffled_a = np.empty(a.shape, dtype=a.dtype)
    shuffled_b = np.empty(b.shape, dtype=b.dtype)
    permutation = np.random.permutation(len(a))
    for old_index, new_index in enumerate(permutation):
        shuffled_a[new_index] = a[old_index]
        shuffled_b[new_index] = b[old_index]
    
    return shuffled_a, shuffled_b

def load_data(sourcePath, steamIDs, timeStep=40, shuffleIt=True, trainSetFraction=0.95):
    """Load data
    Args:
        sourcePath -- The path of the dataset
        steamIDs -- The players' steam ID who the model want to recognize
        timeStep -- The number of time steps in an example
        shuffleIt -- The data need to be shuffled or not
        trainSetFraction -- The percentage of the training set 
    returns:
        X_train -- The training set of X with the shape [data size, time steps, features]
        Y_train -- The training set of Y (one hot) with the shape [data size, num_classes]
        X_test -- The test set of X with the shape [data size, time steps, features]
        Y_test -- The test set of Y (one hot) with the shape [data size, num_classes]
    """
    # Player action files of each match are stored in the same folder 
    # with the same folder name as the original file name of the match, 
    # therefore, we Load all folders in the source folder first.
    folders = [f for f in listdir(sourcePath)] 
    
    # initial a LabelEncoder for all map names in the CS:GO, in order to transform the map name to the cate
    le_map = preprocessing.LabelEncoder()
    le_map.fit(['ar_Baggage','ar_Lake Game','ar_Monastery','ar_Safehouse','ar_Shoots','ar_St. Marc','de_Bank','de_Lake',
    'de_Safehouse','de_Shortdust','de_St. Marc','de_Sugarcane','ar_Dizzy','ar_Lake','ar_Safehouse','ar_Shoots','de_Cobblestone',
    'de_Inferno','de_Lake','de_Rialto','de_Shortdust','de_Train','as_Oilrig','cs_747','cs_Agency','cs_Assault','cs_Backalley','cs_Compound',
    'cs_Downed','cs_Estate','cs_Havana','cs_Insertion','cs_Italy','cs_Miami','cs_Militia','cs_Office','cs_Siege','de_Airstrip','de_Austria',
    'de_Aztec','de_Cache','de_Canals','de_Cobblestone','de_Chateau','de_Corruption','de_Dust','de_Dust II','de_Fastline','de_Mirage','de_Nuke',
    'de_Overpass','de_Piranesi','de_Port','de_Prodigy','de_Shipped','de_Sienna','de_Stadium','de_Storm','de_Survivor','de_Tides','de_Torn','de_Train',
    'de_Truth','de_Vertigo','de_Vostok','Backalley','Cruise','Downtown','Motel','Museum','Rush','Siege','Thunder','Workout',
    'Ali','Bazaar','Black','Castle','Chinatown','Coast','Crashsite','Empire','Facade','Favela','Gwalior','Library',
    'Lite','Log','Marquis','Mikla','Mist','Overgrown','Rails','Resort','Royal','Ruins','Santorini','Seaside',
    'Season','Thrill','Tulip','Zoo'])
    
    steamIDs = np.array(steamIDs)
    
    X = []
    Y = []
    
    for i, folder in enumerate(folders):
        fullFolderName = sourcePath + folder + '/'
        files = glob.glob(path.join(fullFolderName, "*.csv"))
        for i2, file in enumerate(files):
            temp = pd.read_csv(file)
            temp = temp.drop(['Unnamed: 0', 'CurrentTick'], axis=1)
            temp.Map = le_map.fit_transform(temp.Map)
            temp_X = np.array(temp.drop(['SteamID', 'Name'], axis=1))
            #. Resharp the data to (m, timestep, feature)
            for i3 in range(int(len(temp_X)/timeStep)):
                X.append(temp_X[i3*timeStep:i3*timeStep+timeStep,:])
                # As all the data in a file are the same player, we only need to use first row to check the player
                # It means 0 is unknown player, and player label is (1 + his index in SteamIDs)
                idx = np.where(steamIDs == str(temp.SteamID[0]))
                if (np.shape(idx)[1] == 0):
                    Y.append(0)
                else:
                    Y.append(idx[0][0]+1)
                    
    X = np.array(X)
    X = X.astype(np.float)
    Y = np.array(Y)
    Y = np.resize(Y,(len(Y),1)) # Make sure its size is (sample size, 1)
    
    # Transform Y to one hot vector
    ohe = preprocessing.OneHotEncoder()
    ohe.fit(Y)    
    Y = np.array(ohe.transform(Y).toarray())                                                     
    
    # Shuffle X and Y at the same time
    if shuffleIt:
        X, Y = shuffle_in_unison(X, Y)
    
    # Separte X and Y to training set and test set
    NUM_EXAMPLES = int(len(X)*trainSetFraction)
    X_train = X[:NUM_EXAMPLES]
    Y_train = Y[:NUM_EXAMPLES]
    X_test = X[NUM_EXAMPLES:]
    Y_test = Y[NUM_EXAMPLES:]
    
    return X_train, Y_train, X_test, Y_test

def LSTM(X_train, Y_train, X_test, Y_test, epoch=1000, batch_size=64, 
           num_units=128, learning_rate=0.001, restore=False):
    """Simple model with only one layer LSTM and without any mechanism for the regularization
    Args:
        X_train -- Training set of X with the size (training_set_size, time_step, features)
        Y_train -- Training set of Y with the size (training_set_size, num_classes)
        X_test -- Test set of X with the size (training_set_size, time_step, features)
        Y_test -- Test set of Y with the size (training_set_size, num_classes)
        epoch -- The number of epoch (Iteration)
        batch_size -- The size of a batch
        num_units -- The number of the LSTM neurons
        learning_rate -- learning rate
        restore -- restore the weights or not
    """
    g = tf.Graph()
    with g.as_default():
        
        data = tf.placeholder(tf.float32, [None, X_train.shape[1], X_train.shape[2]]) 
        target = tf.placeholder(tf.float32, [None, Y_train.shape[1]])
        lr = tf.placeholder(tf.float32)
      
        # LSTM layer
        cell = tf.contrib.rnn.LSTMCell(num_units,state_is_tuple=True)
        val, state = tf.nn.dynamic_rnn(cell, data, dtype=tf.float32)
        
        # Only take the output activation at the last time step. 
        # It is the same as the val[-1] in python list
        val = tf.transpose(val, [1, 0, 2])
        last = tf.gather(val, int(val.get_shape()[0]) - 1)
        
        # Fully connected Layer
        out_size = target.get_shape()[1].value
        weight = tf.Variable(tf.truncated_normal([num_units, out_size]), name='weights');
        bias = tf.Variable(tf.constant(0.1, shape=[target.get_shape()[1]]), name='bias');
        prediction = tf.nn.softmax(tf.matmul(last, weight) + bias)
        
        # Calculate the cross entropy loss
        loss = -tf.reduce_sum(target * tf.log(tf.clip_by_value(prediction,1e-10,1.0)))
        
        optimizer = tf.train.AdamOptimizer(learning_rate = lr)
        minimize = optimizer.minimize(loss)
        
        # Calculate the number of correct prediction
        num_correct = tf.reduce_sum(tf.cast(tf.equal(tf.argmax(target, 1),tf.argmax(prediction, 1)), tf.float32))
        
        init_op = tf.global_variables_initializer()
        
        saver = tf.train.Saver()
    
    with tf.Session(graph=g) as sess:
        
        # Restore the previous weightes or initial all weights 
        if restore ==False:
            sess.run(init_op)
        else:
            saver.restore(sess, "tmp/model.ckpt")
            
        no_of_batches = int(len(X_train) / batch_size)
        
        for i in range(epoch):
            total_loss = 0
            ptr = 0
            for j in range(no_of_batches):
                inp, out = X_train[ptr:ptr+batch_size], Y_train[ptr:ptr+batch_size]
                ptr+=batch_size
                batch_loss = sess.run([minimize, loss],{data: inp, target: out, lr: learning_rate})[1]
                total_loss += batch_loss
                # Print the progress and some information during the execution of an epoch
                if (j%100 == 0):
                    printStr = "Epoch %i, Processed batch=%.4f, total loss=%.4f" % (i, j/(no_of_batches * 1.), total_loss / (j * 1.))
                    sys.stdout.write ('\r' + printStr)
            
            total_loss /= (no_of_batches * 1.)
            
            # Print the accuracy after the execution of an epoch
            epoch_num_corr = sess.run(num_correct, {data: X_train, target: Y_train})
            epoch_num_corr_test = sess.run(num_correct, {data: X_test, target: Y_test})
            num_train_set = np.shape(Y_train)[0]
            num_test_set = np.shape(Y_test)[0]
            printStr = "Epoch %i, train loss=%.4f, train/test correct= %i / %i, train/test accuracy= %.4f / %.4f" % (i, total_loss, epoch_num_corr, epoch_num_corr_test, (epoch_num_corr/(num_train_set * 1.)), (epoch_num_corr_test/(num_test_set * 1.)))
            sys.stdout.write ('\r' + printStr)
            print ("")
            
            # Save weights every 10 epoches
            if (i%10 == 0):
                saver.save(sess, "tmp/model.ckpt")


def LSTM_1(X_train, Y_train, X_test, Y_test, epoch=1000, batch_size=64, 
               keep_prob=0.6, num_layers=2, num_units=128, learning_rate=0.001, restore=False):
    """It is similar to the simple model but add the functions that you can choose the number of LSTM layers with dropout.
    Args:
        X_train -- Training set of X with the size (training_set_size, time_step, features)
        Y_train -- Training set of Y with the size (training_set_size, num_classes)
        X_test -- Test set of X with the size (training_set_size, time_step, features)
        Y_test -- Test set of Y with the size (training_set_size, num_classes)
        epoch -- The number of epoch (Iteration)
        batch_size -- The size of a batch
        keep_prob -- The rate of neurons you want to keep working (1 - dropout rate)
        num_layers -- The layers of LSTM
        num_units -- The number of the LSTM neurons
        learning_rate -- learning rate
        restore -- restore the weights or not
    """
    g = tf.Graph()
    with g.as_default():
        #the shape of the data is [num_example, time_steps, features]
        data = tf.placeholder(tf.float32, [None, X_train.shape[1], X_train.shape[2]]) 
        target = tf.placeholder(tf.float32, [None, Y_train.shape[1]])
        kp = tf.placeholder(tf.float32)
        lr = tf.placeholder(tf.float32)
      
        # Create LSTM Layers with dropout
        cells = []
        for _ in range(num_layers):
            cell = tf.contrib.rnn.LSTMCell(num_units,state_is_tuple=True)
            cell = tf.contrib.rnn.DropoutWrapper(cell, output_keep_prob=kp)
            cells.append(cell)
        
        cell = tf.contrib.rnn.MultiRNNCell(cells)
        cell = tf.contrib.rnn.DropoutWrapper(cell, output_keep_prob=kp)
        val, state = tf.nn.dynamic_rnn(cell, data, dtype=tf.float32)
        
        # Only take the output activation at the last time step. 
        # It is the same as the val[-1] in python list
        val = tf.transpose(val, [1, 0, 2])
        last = tf.gather(val, int(val.get_shape()[0]) - 1)
        
        # Fully connected Layer
        out_size = target.get_shape()[1].value
        weight = tf.Variable(tf.truncated_normal([num_units, out_size]), name='weights');
        bias = tf.Variable(tf.constant(0.1, shape=[target.get_shape()[1]]), name='bias');
        prediction = tf.nn.softmax(tf.matmul(last, weight) + bias)
        
        # Calculate the cross entropy loss
        loss = -tf.reduce_sum(target * tf.log(tf.clip_by_value(prediction,1e-10,1.0)))
        
        optimizer = tf.train.AdamOptimizer(learning_rate = lr)
        minimize = optimizer.minimize(loss)
        
        # Calculate the number of correct prediction
        num_correct = tf.reduce_sum(tf.cast(tf.equal(tf.argmax(target, 1),tf.argmax(prediction, 1)), tf.float32))
        
        init_op = tf.global_variables_initializer()
        
        saver = tf.train.Saver()
    
    with tf.Session(graph=g) as sess:
        
        # Restore the previous weightes or initial all weights 
        if restore ==False:
            sess.run(init_op)
        else:
            saver.restore(sess, "tmp1/model.ckpt")
         
        no_of_batches = int(len(X_train) / batch_size)
        
        for i in range(epoch):
            total_loss = 0
            ptr = 0
            for j in range(no_of_batches):
                inp, out = X_train[ptr:ptr+batch_size], Y_train[ptr:ptr+batch_size]
                ptr+=batch_size
                batch_loss = sess.run([minimize, loss],{data: inp, target: out, kp: keep_prob, lr: learning_rate})[1]
                total_loss += batch_loss
                
                # Print the progress and some information during the execution of an epoch
                if (j%100 == 0):
                    printStr = "Epoch %i, Processed batch=%.4f, total loss=%.4f" % (i, j/(no_of_batches * 1.), total_loss / (j * 1.))
                    sys.stdout.write ('\r' + printStr)
            
            total_loss /= (no_of_batches * 1.)
  
            # Print the accuracy after the execution of an epoch
            epoch_num_corr = sess.run(num_correct, {data: X_train, target: Y_train, kp: 1})
            epoch_num_corr_test = sess.run(num_correct, {data: X_test, target: Y_test, kp: 1})
            num_train_set = np.shape(Y_train)[0]
            num_test_set = np.shape(Y_test)[0]
            printStr = "Epoch %i, train loss=%.4f, train/test correct= %i / %i, train/test accuracy= %.4f / %.4f" % (i, total_loss, epoch_num_corr, epoch_num_corr_test, (epoch_num_corr/(num_train_set * 1.)), (epoch_num_corr_test/(num_test_set * 1.)))
            sys.stdout.write ('\r' + printStr)
            print ("")
            
            # Save weights every 10 epoches
            if (i%10 == 0):
                saver.save(sess, "tmp1/model.ckpt")