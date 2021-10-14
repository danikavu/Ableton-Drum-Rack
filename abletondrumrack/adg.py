""" Create the '.adg' preset file. """

import os
import gzip
from xml.etree import ElementTree as ET

def write_adg(blank, fname, path):
    """
        Write the adg file.
    """
    blank.write(fname + '.xml')

    with open(fname + '.xml') as new:
        header = '<?xml version="1.0" encoding="UTF-8"?>\n'
        new_data_ = header + new.read()

    f = gzip.open(path + "{}{}.adg".format(os.sep, fname), 'wb')
    f.write(new_data_.encode())
    f.close()
    os.remove(fname + '.xml')


def create_xml(_samples, _pad, choke):
    """
        Creates the xml for the samples and adds them to the empty drum rack.
        Ableton files as it seems are all xml.
    """
    # Open default Drum Rack.
    blank = ET.parse(os.path.dirname(__file__) + '{s}ableton_files{s}blank_drum_rack'.format(s=os.sep))
    blank_root = blank.getroot()
    # Default Choke set to 1.
    _choke = 1
    # Set all the needed values for the adg file not to be corrupt.
    # Filename, File paths, Duration, Size.
    for name, nrp, fp, bp, dur, sz in _samples:
        # Open xml file.
        t = ET.parse(os.path.dirname(__file__) + '{s}ableton_files{s}able_drum_item.xml'.format(s=os.sep))
        r = t.getroot()
        # Pad id. 
        r.attrib['Id'] = str(_pad)
        # Midi key of the pad.
        r.findall('.//ZoneSettings//ReceivingNote')[0].attrib['Value'] = str(_pad)
        # Choke option.
        r.findall('.//ZoneSettings//ChokeGroup')[0].attrib['Value'] = str(_choke)
        # Sample name.
        r.findall('.//MultiSamplePart//Name')[0].attrib['Value'] = name
        # Filepath.
        r.findall('.//FileRef//Path')[1].attrib['Value'] = fp
        r.findall('.//FileRef//Path')[2].attrib['Value'] = fp
        r.findall('.//FileRef//Path')[5].attrib['Value'] = fp
        
        r.findall('.//SampleRef//FileRef//RelativePath')[0].attrib['Value'] = nrp
        r.findall('.//SampleRef//FileRef//RelativePath')[1].attrib['Value'] = nrp
        # File size.
        r.findall('.//SampleRef//OriginalFileSize')[0].attrib['Value'] = str(sz)
        r.findall('.//SampleRef//OriginalFileSize')[1].attrib['Value'] = str(sz)
        # Ableton browser content path.
        r.findall('.//BrowserContentPath')[0].attrib['Value'] = bp
        r.findall('.//BrowserContentPath')[1].attrib['Value'] = bp
        # Sample duration for sustain and release.
        r.findall('.//SampleParts//SampleEnd')[0].attrib['Value'] = str(dur - 1)
        r.findall('.//SampleParts//SustainLoop//End')[0].attrib['Value'] = str(dur - 1)
        r.findall('.//SampleParts//ReleaseLoop//End')[0].attrib['Value'] =str(dur - 1)
        # Sample duration.
        r.findall('.//SampleRef//DefaultDuration')[0].attrib['Value'] = str(dur)
        
        if not choke:
            _choke += 1
        _pad -= 1
        # Append sample data to the empty xml.
        blank_root.findall('.//BranchPresets')[0].append(r)
        
    return blank