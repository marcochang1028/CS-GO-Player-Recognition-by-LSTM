from os import listdir, path, makedirs;
from datetime import datetime;
import sys;
import pandas;
import numpy as np;

def genPlayerActionFiles (sourcePath, processedPath):
    """Transform four files extracted from the demo file into player action files.
        Before read the code, I strongly suggest you to read the "CSGO Player Recognition by RNN (LSTM).pdf" 
        in the Doc folder first. This file can give you the overview of the whole research and some basic 
        knowledge about the CS:GO demo file and output file. All the comments below will assume that you have 
        read the document and had basic knowledge about this research.
        
        The main purpose of this function are as follows:
            a. Merges movement file and other three files.
            b. Decrease the sample size from 128 ticks a second down to 4 tick a second
            c. Separate player actions into different files.
    Args:
        sourcePath -- the path which puts the extracted files
        processedPath -- the path which puts the output files
    """
        
    # Each demo file has four files which put in the folder with the same name as the original demo file.
    folders = [f for f in listdir(sourcePath)];
    
    for folder in folders:
        # The generated player action files from each demo file put in the same folder with the same name as the original demo file
        partProcessedFileName = processedPath + folder; 
        if (not path.exists(partProcessedFileName)):
            print ("######## Strat to process " + folder + " at " + str(datetime.now())[:19] + " ########");
            # Read four extracted files into memory
            partFileName = sourcePath + folder + '/' + folder;
            moveDS = pandas.read_csv(partFileName + '.csv', header=None, names = ['CurrentTick', 'CurrentRound', 'Map', 'SteamID', 'Name', 'Team', 'PositionX', 'PositionY', 'PositionZ', 'VelocityX', 'VelocityY', 'VelocityZ', 'ViewDirectionX', 'ViewDirectionY', 'ActiveWeapon', 'ActionType', 'Hitgroup', 'HitPositionX', 'HitPositionY', 'HitPositionZ']);
            weaponDS = pandas.read_csv(partFileName + '-Weapon.csv', header=None, names = ['CurrentTick', 'SteamID', 'Name', 'ActiveWeapon', 'ActionType']);
            hurtDS = pandas.read_csv(partFileName + '-Hurt.csv', header=None, names = ['CurrentTick', 'SteamID', 'Name', 'ActiveWeapon', 'ActionType', 'Hitgroup', 'HitPositionX', 'HitPositionY', 'HitPositionZ']);
            nadeDS = pandas.read_csv(partFileName + '-Nade.csv', header=None, names = ['CurrentTick', 'SteamID', 'Name', 'ActiveWeapon', 'ActionType', 'HitPositionX', 'HitPositionY', 'HitPositionZ']);
            
            # ###### Process the weapon file #####
            # In this whole prcedure, we go through the whole weaponDS to search the related action in the moveDS 
            # with the same tick and same player name as the weapon action. Then update the fields of 
            # ActiveWeapon and ActionType in this record in the moveDS by the values of the weapon record.
            # As the movement and weapon records both are sequential, we can delete processed records to increase 
            # the performance of the next search procedures
            # ####################################
            
            lastIndex = 0;
            tempDS = moveDS;
            for index, row in weaponDS.iterrows():
                # Start to decrease the size of moveDS to increase the performance after 1280 ticks (10 seconds)    
                if (lastIndex > 1280):        
                    tempDS = moveDS[lastIndex - 1280:];
                
                #.As the copied set will keep original index of parent, we can simply search the index from the downsized tempDS.
                idx = tempDS.loc[lambda df: (df.CurrentTick == row.CurrentTick) & (df.Name == row.Name)].index;
                
                # Update values in the moveDS
                if (len(idx) != 0):
                    idx = idx[0];
                    moveDS.loc[idx, 'ActiveWeapon'] == row.ActiveWeapon;
                    moveDS.loc[idx, 'ActionType'] = row.ActionType;
                    lastIndex = idx; 
                
                if (index % 100 == 0):
                    printStr = "Weapon Processed " + str(int(index/(len(weaponDS) * 1.)*100)) + "%"
                    sys.stdout.write ('\r' + printStr);
                
            printStr = "Weapon Processed 100%"
            sys.stdout.write ('\r' + printStr);
                
            print ("");
            
            # ###### Process the hurt file #####
            # In this whole prcedure, we go through the whole hurtDS to search the related action in the moveDS.
            # As the attack which causes hurt may be earlier than the hurt time but not earlier over 10 seconds, 
            # we start from the current tick in the moveDS and move back at most 1280 ticks earlier (1 second is 128 ticks) 
            # to find the belonging tick of attack. Then update several fields in this record in the moveDS
            #by the values of the hurt record.
            # As the movement and hurt records both are sequential, we can delete processed records to increase 
            # the performance of the next search action
            # ####################################
            tempDS = moveDS;
            lastIndex = 0;
            for index, row in hurtDS.iterrows():
                # Start to decrease the size of moveDS to increase the performance after certain ticks 
                # We choose 12800 because we want to make sure we will only start to decrease data over 10 seconds.
                # (If we have 10 users in this game and 128 ticks per second, then the records of 10 seconds is 12800)
                if (lastIndex > 12800):
                    tempDS = moveDS[lastIndex - 12800:];
                
                #.As the copied set will keep original index of parent, we can simply search the index from the downsized tempDS.
                idx = tempDS.loc[lambda df: (df.CurrentTick == row.CurrentTick) & (df.Name == row.Name)].index;
                
                if (len(idx) == 0):
                        break;
                else:
                    idx = idx[0];
                
                #. Search the belonging record in the moveDS within the region between the current tick and the (current ticks - 10 seconds) 
                startIndex = 0;
                if (idx > 12800):
                    startIndex = idx-12800;
                searchDS = moveDS[startIndex:idx+1][lambda df: (df.Name == row.Name)];
                searchDS = searchDS.sort_index(axis=0, ascending=False);
                
                for lastIndex, lastRow in searchDS.iterrows():
                    #. Update values in the moveDS
                    if (lastRow.ActiveWeapon == row.ActiveWeapon):
                        moveDS.loc[lastIndex, 'ActionType'] = row.ActionType;
                        moveDS.loc[lastIndex, 'Hitgroup'] = row.Hitgroup;
                        moveDS.loc[lastIndex, 'HitPositionX'] = row.HitPositionX;
                        moveDS.loc[lastIndex, 'HitPositionY'] = row.HitPositionY;
                        moveDS.loc[lastIndex, 'HitPositionZ'] = row.HitPositionZ;
                        break;
                
                lastIndex = idx;
                
                if (index % 100 == 0):
                    printStr = "Hurt Processed " + str(int(index/(len(hurtDS) * 1.)*100)) + "%"
                    sys.stdout.write ('\r' + printStr);
                
            printStr = "Hurt Processed 100%"
            sys.stdout.write ('\r' + printStr);
                
            print ("");
            
            # ###### Process the nade landing file #####
            # Exactly the same idea as the hurt file
            # ####################################
            lastIndex = 0;
            tempDS = moveDS;
            for index, row in nadeDS.iterrows():
                # Start to decrease the size of moveDS to increase the performance
                if (lastIndex > 12800):
                    tempDS = moveDS[lastIndex - 12800:];
                
                #.As the copied set will keep original index of parent, we can simply search the index from the downsized tempDS.
                idx = tempDS.loc[lambda df: (df.CurrentTick == row.CurrentTick) & (df.Name == row.Name)].index;
                
                if (len(idx) == 0):
                        break;
                else:
                    idx = idx[0];
                
                #. Search the belonging record in the moveDS within the region between the current tick and the (current ticks - 10 seconds) 
                startIndex = 0;
                if (idx > 12800):
                    startIndex = idx-12800;
                searchDS = moveDS[startIndex:idx+1][lambda df: (df.Name == row.Name)];
                searchDS = searchDS.sort_index(axis=0, ascending=False);
                
                for lastIndex, lastRow in searchDS.iterrows():
                    #. Update values in the moveDS
                    if (lastRow.ActiveWeapon == row.ActiveWeapon):
                        moveDS.loc[lastIndex, 'ActionType'] = row.ActionType;
                        moveDS.loc[lastIndex, 'HitPositionX'] = row.HitPositionX;
                        moveDS.loc[lastIndex, 'HitPositionY'] = row.HitPositionY;
                        moveDS.loc[lastIndex, 'HitPositionZ'] = row.HitPositionZ;
                        break;
                
                lastIndex = idx;
            
                if (index % 100 == 0):
                    printStr = "Nade Processed " + str(int(index/(len(nadeDS) * 1.)*100)) + "%"
                    sys.stdout.write ('\r' + printStr);
            
            printStr = "Nade Processed 100%"
            sys.stdout.write ('\r' + printStr);
                
            print ("");
                
            ########### Decrease the sample size and separate records to different players. #########
            # Decrease the data size from 128 ticks per second to 4 ticks per second and transfer it from panda to numpy array.
            # That is to say, every 32 records merge to 1 records. In this procedure, the program checks the action type
            # and only leave the action type with higher value (0: move, 1: fired, 2: hurtNotByNade, 3: hurtByNade). 
            # As it is impossibel players can do two things within 1/4 second, it will not happen to merge two records with action type 2 and 3 together.
            ################################################################################################
            print ("start to decrease the data");
            players = moveDS.Name.unique(); # Find all names of players 
            
            #Initial the dictionaries for players
            allPlayersDic = {};
            allPlayerIndexsDic = {};
            allPlayerStartTick = {};
            for player in players:
                allPlayersDic[player] = pandas.DataFrame(columns = ['CurrentTick', 'CurrentRound', 'Map', 'SteamID', 'Name', 'Team', 'PositionX', 'PositionY', 'PositionZ', 'VelocityX', 'VelocityY', 'VelocityZ', 'ViewDirectionX', 'ViewDirectionY', 'ActiveWeapon', 'ActionType', 'Hitgroup', 'HitPositionX', 'HitPositionY', 'HitPositionZ']);
                allPlayerIndexsDic[player] = 0;
                firstRowOfPlayer = moveDS[moveDS.Name == player].iloc[0];
                allPlayerStartTick[player] = firstRowOfPlayer.CurrentTick;
            
            # Start to downsize and separate players at the sametime. 
            totalRows = len(moveDS);
            for index, row in moveDS.iterrows():
                if (index % 5000) == 0:
                    printStr = "Processed " + str(int(index/(totalRows * 1.)*100)) + "%"
                    sys.stdout.write ('\r' + printStr);
                key = row.Name;
                if ((row.CurrentTick-allPlayerStartTick[key]) % 32) == 0:
                    if (row.CurrentTick != allPlayerStartTick[key]):
                        allPlayerIndexsDic[key] += 1;
                    playerRecords = allPlayersDic[key];
                    playerRecords.loc[allPlayerIndexsDic[key]] = row;
                else:
                    playerRecords = allPlayersDic[key];
                    record = playerRecords.loc[allPlayerIndexsDic[key]];
                    if (record.ActionType < row.ActionType):
                        playerRecords.loc[allPlayerIndexsDic[key]] = row;
            
            printStr = "Processed 100%"
            sys.stdout.write ('\r' + printStr);
            
            makedirs(partProcessedFileName);
            
            for i, (k, v) in enumerate(allPlayersDic.items()):
                v.to_csv(partProcessedFileName + '/' + folder + '-' + v.loc[0].Name + '.csv');
            
            print ("");
            print ("######## The process of " + folder + " was completed at " + str(datetime.now())[:19] + " ########");
            
        else:
            print ("######## " + folder +" was processed ########");
