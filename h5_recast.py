"""
This script will recast the data type of a dataset in an HDF5 file from 64 bit to 32 bit.
"""

import os
import h5py
import numpy as np
from argparse import ArgumentParser

def downcast_dtype(data):
    """
    Downcast 64-bit data types to 32-bit.

    Parameters
    ----------
    data : np.array
        The data to downcast.

    Returns
    -------
    np.array
        The downcasted data.
    """
    if data.dtype == np.float64:
        return data.astype(np.float32)
    elif data.dtype == np.int64:
        return data.astype(np.int32)
    else:
        return data
    
def copy_and_downcast(source: h5py.File, destination: h5py.File) -> None:
    """
    Copy datasets from the source file to the destination file, downcasting 64-bit data types to 32-bit.

    Parameters
    ----------
    source : h5py.File
        The source HDF5 file.

    destination : h5py.File
        The destination HDF5 file.
    """
    def _copy_dataset(name, obj):
        if isinstance(obj, h5py.Dataset):
            data = obj[...]
            downcasted_data = downcast_dtype(data)
            destination.create_dataset(name, data=downcasted_data)
        elif isinstance(obj, h5py.Group):
            destination.create_group(name)

    source.visititems(_copy_dataset)

if __name__ == "__main__":
    parser = ArgumentParser(
        description="Combine HDF5 files and downcast 64-bit data to 32-bit"
        )
    parser.add_argument(
        "input_file",
        help="The name of the input file", metavar="INPUT_FILE"
        )
    parser.add_argument(
        "output_file",
        help="The name of the output file", metavar="OUTPUT_FILE"
        )
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file

    confirm = input("Do you want to recast these files? (Y/n): ")
    if confirm.lower() != 'n':
        print("Recasting files...")

        with h5py.File(os.path(output_file), 'w') as dest:
            with h5py.File(os.path(input_file), 'r') as src:
                copy_and_downcast(src, dest)

        print("Files recast into:", output_file)
    else:
        print("Recast cancelled. Exiting..")