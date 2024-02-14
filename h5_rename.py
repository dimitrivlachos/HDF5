'''
A script to a set of files pertaining to a specific experiment. The files are in the form of .h5 files and are named in the following format:
    - '{prefix}.run'
    - '{prefix}_1.nxs'
    - '{prefix}_1_000001.h5'
    - '{prefix}_1_header.cbf'
    - '{prefix}_1_master.h5'
    - '{prefix}_1_meta.h5'

The script will rename the files to the following format:
    - '{new prefix}.run'
    - '{new prefix}_1.nxs'
    - '{new prefix}_1_000001.h5'
    - '{new prefix}_1_header.cbf'
    - '{new prefix}_1_master.h5'
    - '{new prefix}_1_meta.h5'

The script will also update the internal metadata of the .h5 files to reflect the new prefix.
The script will also update the .nxs file to reflect the new prefix.
'''

import h5py
import os

def find_files_with_prefix(directory, prefix):
    '''
    Find files in a directory that start with a specific prefix.

    Parameters
    ----------
    directory : str
        The directory to search for files.

    prefix : str
        The prefix to search for.

    Returns
    -------

    matching_files : list
        A list of files in the directory that start with the specified prefix.
    '''
    matching_files = []
    for filename in os.listdir(directory):
        if filename.startswith(prefix):
            matching_files.append(filename)
    return matching_files