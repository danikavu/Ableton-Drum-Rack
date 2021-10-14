""" This file handles Hashing, SQL, Frames, Duration. """

import os
import hashlib
import sqlite3
import numpy as np
import pandas as pd
import soundfile as sf

# https://www.ibm.com/docs/en/zos/2.3.0?topic=attributes-block-size-record-length
BLOCK_SIZE = 65536
# Default db path
DB_PATH = os.path.expanduser("~") + '{}ableton_samples.db'.format(os.sep)


def sample_hash(path):
    # Currently not used
    """
        Create md5 hash for sample file.
    """
    
    file_hash = hashlib.md5() 
    with open(path, 'rb') as file:
        fileblock = file.read(BLOCK_SIZE)
        while len(fileblock) > 0:
            file_hash.update(fileblock)
            fileblock = file.read(BLOCK_SIZE)

    return file_hash.hexdigest()
    

def sample_characteristics(path, loginfo):
    """
        Get frames and duration of sample.
        If logging true store data in database.
    """
    # If extraction fails set sample to not supported.
    try:
        f = sf.SoundFile(path)
        duration = f.frames / f.samplerate
        if loginfo:
            update_frames_length(f.frames, duration, path)
            
        return f.frames, duration
        
    except Exception as e:
        connection = sqlite3.connect(DB_PATH)
        cur = connection.cursor()
        cur.execute('UPDATE SAMPLE_PATHS SET SUPPORTED = 0 WHERE FULL_FILE_PATH = "{}"'.format(path))
        connection.commit()
        connection.close() 


def sample_size(path):
    """
        Get sample file size.
    """
    return os.path.getsize(path)     


def create_sample_df(path):
    """
        Get all sample paths inside the given folder.
        Only looks for wav files.
    """
    # Get full paths for samples.
    dirs = [folder[0] for folder in os.walk(path)]
    # Unacceptable.
    dirs = [x for x in dirs if len([x for x in os.listdir(x) if '.wav' in x])]

    folder_path, sample_name, ff_path, folder_name = [], [], [], []

    for _path in dirs:
        for _sample in os.listdir(_path):
            if _sample.endswith('.wav') and _sample[0] != '.':
                full_sample_path = _path + '\\' + _sample
                ff_path.append(full_sample_path)
                folder_path.append(_path)
                folder_name.append(_path.split('\\')[-1])
                sample_name.append(_sample)
    # Create a dataframe                 
    dirs_add = pd.DataFrame(
        {'FOLDER_PATH': folder_path,
         'FOLDER_NAME': folder_name,
         'SAMPLE_NAME': sample_name, 
         'FULL_FILE_PATH': ff_path,
         }
    )
    # Add empty columns for updates later on. Currently time consuming on build if many samples provided.
    dirs_add['SAMPLE_SIZE'] = np.nan
    dirs_add['FRAMES'] = np.nan
    dirs_add['LENGTH'] = np.nan
    dirs_add['SAMPLE_HASH'] = np.nan
    dirs_add['SUPPORTED'] = np.nan
    
    return dirs_add
    
#######################
## Sqlite3 functions ##
#######################


def query(_query):
    """
        Takes query inputs from user.
    """
    try:
        connection = sqlite3.connect(DB_PATH)
        result = pd.read_sql(_query, connection)
        connection.close()
        
        if result.empty:
            raise ValueError('No samples found for query')
            
        return result
        
    except Exception as e:
        if 'no such table' in str(e):
            print('Database or Table not Found')
        else:
            print(e)


def update_frames_length(f, d, p):
    """
        Update sample in database for frames and duration.
    """
    connection = sqlite3.connect(DB_PATH)
    cur = connection.cursor()
    cur.execute('UPDATE SAMPLE_PATHS SET FRAMES = {}, LENGTH = {} WHERE FULL_FILE_PATH = "{}"'.format(f, d, p))
    connection.commit()
    connection.close()    
    

def create_sample_database(path):
    """
        Creates a database for the samples in a given path.
        All subdirectories in path are included.
    """
    if 'ableton_samples.db' in os.listdir(os.path.expanduser("~")):
        # Make sure user wants to recreate if database exists. It's time consuming.
        _input = input('Database already exists. Do you want to overwrite? y/n:')
        if _input == 'y':
            samples_df = create_sample_df(path)
            connection = sqlite3.connect(os.path.expanduser("~") + '{}ableton_samples.db'.format(os.sep))
            samples_df.to_sql('SAMPLE_PATHS', connection, if_exists='replace', index=False)
            connection.close()
            
            return 'Database Succesfully Created'
    else:
        samples_df = create_sample_df(path)
        connection = sqlite3.connect(os.path.expanduser("~") + '{}ableton_samples.db'.format(os.sep))
        samples_df.to_sql('SAMPLE_PATHS', connection, if_exists='replace', index=False)
        connection.close()
        
        return 'Database Succesfully Created'
        
        
def update_sample_details(path=False):
    """
        Update frames, duration for samples given a path or the full database.
        !!! Warning a full database update may take some time depending on the amount of samples.
    """
    if path:
        z = "select * from SAMPLE_PATHS where FULL_FILE_PATH LIKE '%{}%' AND LENGTH IS NULL".format(path)
        sample_types = query(z)
        for i ,r in sample_types.iterrows():
            sample_characteristics(r['FULL_FILE_PATH'], loginfo=True)
    else:
        z = "select * from SAMPLE_PATHS AND LENGTH IS NULL"
        sample_types = query(z)
        for i ,r in sample_types.iterrows():
            sample_characteristics(r['FULL_FILE_PATH'], loginfo=True)
            

def add_new_samples(path):
    """
        Inserts samples from a given a path.
    """
    samples_df = create_sample_df(path)
    connection = sqlite3.connect(os.path.expanduser("~") + '{}ableton_samples.db'.format(os.sep))
    samples_df.to_sql('SAMPLE_PATHS', connection, if_exists='append', index=False)
    connection.close()