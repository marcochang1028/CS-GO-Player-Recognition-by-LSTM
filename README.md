# CS-GO-Player-Recognition
An ongoing research project to study the human behaviour by the application of CS:GO Pro Player Recognition by RNN (LSTM).

## Objective
Use the RNN (LSTM) to find players' behaviour patterns from the CS:GO in-game playing data and can further recognize players. Please note that it is an ongoing project, everything I explained below might be changed over time, especially the structure of the model and the setting of the parameters (Such as the number of time steps in an example).


## Concept of the Model
As the players' actions are a time series, we decided to use the LSTM model to recognize players. The main steps are as follows:
1. Four different kinds of in-game playing data (Movement, Fired, Hurt, Grenade landing) were exported from the recorded matches of game CS:GO (it is called Demo file).
2. Four in-game playing data were merged, downsized and separated into the files of different players. 
3. the data were reconstructed and reshaped to three dimensions data with 40 time steps (10 second actions) and fed it into the LSTM network to train the models to recognize players. 

A pdf file in the folder `Doc/` has a detailed description of the project. Please read it to get some basic knowledge about the CS:GO demo file and output files, especially if you want to read the code of data preprocessing.  

## Challenges of the Data
1. How to merge Movement, Fired, Hurt, Grenade landing files into one file and keep the correlation between these actions? The solution we proposed is explained in the pdf file in the Doc folder.
2. In the Demo file, 1 second has 128 records for a player, therefore, only a demo file with 10 players will generate over 1 million records in the Movement file. If we keep this size and feed it into the LSTM, the time steps will be too much for a length of 10 seconds (around 1280 time steps), thus, we decided to merge the records from 128 records per second to 4 records per second despite some information losses.

## Running Test
1. A match record files is called demo files in the CS:GO. It can be downloaded from [HLTV](https://www.hltv.org/) or two files in my folder `TestData/Raw/` for the testing.
2. Execute the program `CSGODemoParser.exe` in the folder `Data Preprocessing/CSGODemoParser_Release/`. Change the input and output path. Push the button `Parser Demos`. 
  - If you want to export records of all round in demo files, please change the value in the field `ParserMaxRound` to a big number (like 100).
  - A demo file generates four files Movement.csv, Fired.csv, Hurt.csv and Grenade.csv which are put into a folder with the same name as the original demo file. A generated files from two demo files mentioned above are put in the folder `Test Data/FirstOutput/` for the testing. (as the data size is huge, I only generated 3 rounds data from each demo file)
  - A C# library [DemoInfo](https://github.com/StatsHelix/demoinfo) is used to parse the demo files.
  - The source code of this program is in the folder `Data Preprocessing/CSGODemoParser/`
3. Execute the function `genPlayerActionFiles` in the file `GenPlayerActionFiles.py` in the folder `Data Preprocessing/` to merge and downsize four files and then separate it into different players' action files.
  - The players' action files are put into a folder with the same name as the original demo file.
  - The final processed files are put in the folder `Test Data/Processed/`. They were generated from 17 demo files.
4. Execute the function 'load_data' in the file `TF_LSTM_Player.py` in the folder `LSTM` with the script as follows:
```
import TF_LSTM_Player as tlp
import numpy as np
# Please note that players are randomly selected from the dataset
# Niko, LETN1, GuardiaN, nekiz, nitr0, rain, xccurate, XigN, jayzaR, Hiko
steamIDs = np.array(['76561198041683378', '76561198042092011', '76561197972331023', '76561198036884160', '76561197995889730', 
                    '76561197997351207', '76561198137694535', '76561198010075210', '76561197987452984', '76561197960268519'])

# The timeStep is a hyper-parameter, you can try 40 or any number.
X_train, Y_train, X_test, Y_test = tlp.load_data('Processed/', steamIDs, timeStep=20, 
                                                 shuffleIt=True, trainSetFraction=0.95)
```
5. Execute the function 'LSTM_1' or 'LSTM' in the file `TF_LSTM_Player.py` in the folder `LSTM` with the script as follows:
```
#. Simple model only implement 1 layer without dropout
tlp.LSTM(X_train, Y_train, X_test, Y_test, epoch=10000, batch_size=64, num_units=200, learning_rate=0.0001, restore=True)

#. The model which you can choose the number of layers and dropout rate.
tlp.LSTM_1(X_train, Y_train, X_test, Y_test, epoch=10000, batch_size=64, 
           keep_prob=0.6, num_layers=2, num_units=200, learning_rate=0.0001, restore=True)
```

# References
<TBD>
  
# Remarks
<TBD>
