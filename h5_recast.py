import os
import shutil
import h5py
import numpy as np
from argparse import ArgumentParser
from typing import List

def find_files_with_prefix(directory: str, prefix: str) -> List[str]:
    """
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
    """
    print(f"Searching for files with prefix: {prefix} in directory: {directory}")
    
    matching_files = []
    try:
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.name.startswith(prefix):
                    matching_files.append(entry.name)
    except OSError as e:
        print(f"Error: {e}")
    return matching_files

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

def copy_and_downcast(source_file: str, dest_file: str) -> None:
    """
    Copy datasets from the source file to the destination file, downcasting 64-bit data types to 32-bit.

    Parameters
    ----------
    source_file : str
        The source HDF5 file path.

    dest_file : str
        The destination HDF5 file path.
    """
    with h5py.File(source_file, 'r') as src, h5py.File(dest_file, 'w') as dest:
        def _copy_dataset(name, obj):
            if isinstance(obj, h5py.Dataset):
                shape = obj.shape
                dtype = obj.dtype
                maxshape = obj.maxshape
                chunks = obj.chunks

                if dtype == np.float64:
                    new_dtype = np.float32
                elif dtype == np.int64:
                    new_dtype = np.int32
                else:
                    new_dtype = dtype

                dest_dataset = dest.create_dataset(name, shape=shape, dtype=new_dtype, maxshape=maxshape, chunks=chunks)

                if chunks:
                    # Read and write in chunks, taking care of the dataset dimensions
                    it = np.nditer(np.zeros(shape), flags=['multi_index'])
                    for _ in it:
                        idx = it.multi_index
                        chunk_slices = tuple(slice(idx[dim], idx[dim] + chunks[dim]) for dim in range(len(chunks)))
                        chunk_data = obj[chunk_slices]
                        dest_dataset[chunk_slices] = downcast_dtype(chunk_data)
                else:
                    data = obj[...]
                    dest_dataset[...] = downcast_dtype(data)

            elif isinstance(obj, h5py.Group):
                dest.create_group(name)

        src.visititems(_copy_dataset)

def search_and_replace(source: h5py.Group, file_mappings: dict) -> None:
    """
    Recursively search through an HDF5 file and replace the old prefix with the new prefix.

    Parameters
    ----------
    source : h5py.Group
        The root group of the HDF5 file to search through.

    file_mappings : dict
        A dictionary containing the old file names as keys and the new file names as values.

    Returns
    -------
    None
    """
    def _visit(name):
        if source.get(name, getclass=True) is h5py.Dataset:
            return
        group = source[name]
        for key in group:
            link = group.get(key, getlink=True)
            if isinstance(link, h5py.ExternalLink):
                if link.filename in file_mappings:
                    new_filename = file_mappings[link.filename]
                    new_path = link.path.replace(link.filename, new_filename)
                    del group[key]
                    group[key] = h5py.ExternalLink(file_mappings[link.filename], link.path)
                    
    source.visit(_visit)

def fix_external_links(directory: str, file_mappings: dict) -> None:
    """
    Searches files for external links, deletes the old links and replaces them with new links.

    Parameters
    ----------
    directory : str
        The directory to search for files.

    file_mappings : dict
        A dictionary containing the old file names as keys and the new file names as values.

    Returns
    -------
    None
    """    
    for file in file_mappings.keys():
        if not file.endswith(".h5") and not file.endswith(".nxs"):
            continue
        file_path = os.path.join(directory, file_mappings[file])
        with h5py.File(file_path, "r+") as f:
            search_and_replace(f, file_mappings)

def batch_copy_and_downcast(source_dir: str, dest_dir: str, file_mappings: dict) -> None:
    """
    Copy and downcast a set of files from the source directory to the destination directory.

    Parameters
    ----------
    source_dir : str
        The directory containing the source files.

    dest_dir : str
        The directory to save the copied and downcast files.

    file_mappings : dict
        A dictionary containing the old file names as keys and the new file names as values.
    """
    for old_name, new_name in file_mappings.items():
        old_path = os.path.join(source_dir, old_name)
        new_path = os.path.join(dest_dir, new_name)
        try:
            copy_and_downcast(old_path, new_path)
        except OSError as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    file_mappings = {}

    parser = ArgumentParser(
        description="Rename a set of files with a given prefix"
        )
    parser.add_argument(
        "source_directory", 
        help="The source directory containing the files", metavar="SOURCE_DIRECTORY"
        )
    parser.add_argument(
        "destination_directory", 
        help="The destination directory to save the renamed files", metavar="DESTINATION_DIRECTORY"
        )
    parser.add_argument(
        "prefix", 
        help="The prefix to search for", metavar="PREFIX"
        )
    parser.add_argument(
        "new_prefix", 
        help="The new prefix to rename the files to", metavar="NEW_PREFIX"
        )
    args = parser.parse_args()

    source_directory = args.source_directory
    destination_directory = args.destination_directory
    prefix = args.prefix
    new_prefix = args.new_prefix

    matching_files = find_files_with_prefix(source_directory, prefix)

    if not matching_files:
        print(f"No files found with prefix: {prefix}")
        exit(1)

    for file in matching_files:
        updated_name = file.replace(prefix, new_prefix)
        file_mappings[file] = updated_name

    print("Found matching files:")
    for old_name, new_name in file_mappings.items():
        print(f"{old_name.ljust(20)}->\t{new_name}")
    confirm = input("Do you want to rename these files? (Y/n): ")
    if confirm.lower() != 'n':
        print("Renaming files...")
        os.makedirs(destination_directory, exist_ok=True)
        batch_copy_and_downcast(source_directory, destination_directory, file_mappings)
        fix_external_links(destination_directory, file_mappings)
        print("Files renamed, downcasted, and links updated.")
    else:
        print("Rename cancelled. Exiting..")
