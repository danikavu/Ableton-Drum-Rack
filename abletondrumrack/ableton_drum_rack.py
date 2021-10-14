""" Creates A Drum Rack preset for Ableton Live 11"""

import os
import pandas as pd
import random
from .tools import *
from .adg import *


# System random to pick samples
SYS_RAND = random.SystemRandom()
# Default Drum Rack pad setup.
DEFAULT_PADS = {
    'pad1': 'kick',
    'pad2': '|'.join(['perc', 'clap', 'rim', 'snap']),
    'pad3': 'snare',
    'pad4': '|'.join(['perc', 'clap', 'snare']),
    'pad5': 'snare',
    'pad6': '|'.join(['bass', '808']),
    'pad7': r'^(?=.*hi)(?=.*hat)',
    'pad8': '|'.join(['bass', '808','sub']),
    'pad9': r'^(?=.*hi)(?=.*hat)',
    'pad10': '|'.join(['fx', 'synth', 'stab']),
    'pad11': r'^(?=.*open)(?=.*hat)',
    'pad12': 'tom',
    'pad13': 'bass',
    'pad14': '|'.join(['fx', 'synth', 'stab']),
    'pad15': '|'.join(['fx', 'synth', 'stab']),
    'pad16': '|'.join(['fx', 'synth', 'stab']),
}


class DrumRack:

    save_path = os.path.expanduser("~")
    default_pads = DEFAULT_PADS

    def __init__(self):
        pass

        
    def new_samples(self, new_list, sample_df, loginfo):
        """
            Create required fields for Ableton's xml file given a list of samples.
        """
        new_sample_name = []
        new_relative_path_samples = []
        new_path_samples = []
        new_browser_content_path = []
        new_duration = []
        new_file_size = []
        
        for num in new_list:
            fp = sample_df.loc[num]['FULL_FILE_PATH'].replace(' ', '%20').split('\\')
            sample_name = sample_df.loc[num]['SAMPLE_NAME'].split('.')[0]
            file_path = '../../../' + sample_df.loc[num]['FULL_FILE_PATH'][3:]
            real_file_path = sample_df.loc[num]['FULL_FILE_PATH']
            ableton_file_path = 'userfolder:' + fp[0] + '%5C' + fp[1] + '%5C#' + fp[2] + ':' +  ':'.join(fp[3:])
            # If frame and duration provided in samle database use existing data, else try to extract.
            if not pd.isnull(sample_df.loc[num]['FRAMES']):
                duration = int(sample_df.loc[num]['FRAMES'])
            else:
                try:
                    duration = sample_characteristics(sample_df.loc[num]['FULL_FILE_PATH'], loginfo)[0]
                except:
                    duration = 0
                
            filesize = os.path.getsize(sample_df.loc[num]['FULL_FILE_PATH'])
            new_duration.append(duration)
            new_file_size.append(filesize)
            new_sample_name.append(sample_name)
            new_relative_path_samples.append(file_path)
            new_path_samples.append(real_file_path)
            new_browser_content_path.append(ableton_file_path)
            
        return new_sample_name, new_relative_path_samples, new_path_samples, new_browser_content_path, new_duration, new_file_size  


    def make_drum_rack(self, samples, slots=16, fname=False, pad=128, loginfo=False, choke=False):
        """
            Makes a Drum Rack. 
            User can specify number of pads to fill.
        """
        
        if pad > 128:
            raise ValueError('Max pad number is 128')
            
        if slots > pad:
            raise ValueError('Not enough slots!\nMax slots for selected pads [{}] is {}'.format(pad, pad))
            
        random_samples = [SYS_RAND.randint(0, len(samples) - 1) for x in range(slots)]
        n_name, n_rel_path, n_f_path, n_browser, n_duration, n_filesize = self.new_samples(random_samples, samples, loginfo)
        _samples = list(zip(n_name, n_rel_path, n_f_path, n_browser, n_duration, n_filesize))
        
        blank = create_xml(_samples, pad, choke)
        
        if not fname:
            fname = 'python_drum_rack'
            
        write_adg(blank, fname, self.save_path)
        
        return 'Succesfully created preset {}'.format(fname)


    def make_default_drum_rack(self, samples=None, loginfo=False, fname=False, choke=False):
        """
            Makes a Drum Rack that 'mimics' the default Ableton Drum Rack and sample positions.
            Uses the DEFAULT_PADS.
        """
        
        if samples is None:
            _query = "SELECT * FROM SAMPLE_PATHS WHERE SUPPORTED IS NULL"
            sample_types = query(_query)
        else:
            sample_types = samples
        
        pad = 92
        
        random_samples = []
        for rack_pad in self.default_pads.items():
            _samples_ = list(sample_types.loc[sample_types['SAMPLE_NAME'].str.contains('{}'.format(rack_pad[1]), case=False)].index)
            if not _samples_:
                random_samples.append(SYS_RAND.choice(sample_types.index))
            else:
                random_samples.append(SYS_RAND.choice(_samples_))

        n_name, n_rel_path, n_f_path, n_browser, n_duration, n_filesize = self.new_samples(random_samples, sample_types, loginfo)
        _samples = list(zip(n_name, n_rel_path, n_f_path, n_browser, n_duration, n_filesize))

        blank = create_xml(_samples, pad, choke)
        
        if not fname:
            fname = 'python_drum_rack_def'
            
        write_adg(blank, fname, self.save_path)
        
        return 'Succesfully created preset {}'.format(fname)


