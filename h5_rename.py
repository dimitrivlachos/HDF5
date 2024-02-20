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
The script will also update the .nxs and .run files to reflect the new prefix.
'''

from argparse import ArgumentParser
import h5py
import os
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
        # Use os.scandir() to get a list of files in the directory
        # This is more efficient than os.listdir() as it returns an iterator
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.name.startswith(prefix):
                    matching_files.append(entry.name)
    except OSError as e:
        print(f"Error: {e}")
    return matching_files

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
        # visit() will only return hardlink Datasets and Groups, non-recursively
        if source.get(name, getclass=True) is h5py.Dataset:
            return
        # We need to manually walk this group to check for external links
        group = source[name]
        for key in group:
            link = group.get(key, getlink=True)
            if isinstance(link, h5py.ExternalLink):
                # Check if the file is in the mapping
                if link.filename in file_mappings:
                    # Replace the old prefix with the new prefix
                    new_filename = file_mappings[link.filename]
                    new_path = link.path.replace(link.filename, new_filename)
                    # Update the link
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
            continue # Skip files that are not .h5 or .nxs files
        file_path = os.path.join(directory, file_mappings[file])
        with h5py.File(file_path, "r+") as f:
            search_and_replace(f, file_mappings)

def batch_rename(directory: str, file_mappings: dict) -> None:
    """
    Rename a set of files in a directory.

    Parameters
    ----------
    directory : str
        The directory containing the files to rename.

    file_mappings : dict
        A dictionary containing the old file names as keys and the new file names as values.
    """
    for old_name, new_name in file_mappings.items():
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        try:
            os.rename(old_path, new_path)
        except OSError as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Dict storing old names and new names
    file_mappings = {}

    # Parse the command line arguments
    parser = ArgumentParser(
        description="Rename a set of files with a given prefix"
        )
    parser.add_argument(
        "directory", 
        help="The directory containing the files", metavar="DIRECTORY"
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

    # Get the command line arguments
    directory = args.directory
    prefix = args.prefix
    new_prefix = args.new_prefix

    # Find the files with the specified prefix
    matching_files = find_files_with_prefix(directory, prefix)

    if not matching_files:
        print(f"No files found with prefix: {prefix}")
        exit(1)

    # Generate a mapping of old names to new names
    for file in matching_files:
        # Generate the new name
        updated_name = file.replace(prefix, new_prefix)
        file_mappings[file] = updated_name

    # Print the matching files and ask for confirmation
    print("Found matching files:")
    for old_name, new_name in file_mappings.items():
        print(f"{old_name.ljust(20)}->\t{new_name}")
    confirm = input("Do you want to rename these files? (Y/n): ")
    if confirm.lower() != 'n':
        print("Renaming files...")
        # Rename the files
        batch_rename(directory, file_mappings)
        # Fix the external links
        fix_external_links(directory, file_mappings)
        print("Files renamed, links updated.")
    else:
        print("Rename cancelled. Exiting..")
