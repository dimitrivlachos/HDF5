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

def duplicate_hdf5(source: h5py.Group, target: h5py.Group) -> None:
    """
    Copy all local contents of an HDF5 file to another HDF5 file.

    Parameters
    ----------
    source : h5py.File
        The source HDF5 file.

    target : h5py.File
        The target HDF5 file.

    Returns
    -------
    None
    """
    # Recursively copy the objects from the source to the target
    def copy(name):
        print(f"Visiting {name}")
        
        if source.get(name, getclass=True) is h5py.Dataset:
            print(f"Copying {name} as dataset")
            target.copy(source[name], name)
            return
        elif source.get(name, getclass=True) is h5py.Group:
            if not isinstance(source[name], h5py.ExternalLink):
                print(f"Creating group {name}")
                target.create_group(name)

                # Copy attributes
                for key, value in source[name].attrs.items():
                    target[name].attrs[key] = value

    source.visit(copy)

def update_external_links(source: h5py.Group, target: h5py.Group, file_mappings: dict) -> None:
    """
    Remap all external links in an HDF5 file to point to new files.
    """
    def update_link(name):
        print(f"Visiting {name}")
        if source.get(name, getclass=True) is h5py.Dataset:
            print(f"Skipping {name} because it is a dataset")
            return

        # Manually walk through group to find external links
        group = source[name]
        for key in group:
            print(f"Checking {key} in {name}")
            link = group.get(key, getlink=True)
            if isinstance(link, h5py.ExternalLink):
                print(f"Found external link to {link.filename} at {link.path}")
                # Create a new external link in the target file
                if key not in target[name]:
                    new_filename = file_mappings.get(link.filename)
                    new_path = link.path.replace(link.filename, new_filename)
                    print(f"Creating external link to {new_filename} at {new_path}")
                    target[key] = h5py.ExternalLink(new_filename, new_path)

    source.visit(update_link)


def duplicate_wrapper(directory: str, file: str, file_mappings: dict) -> None:
    """
    Given an HDF5 file, returns the filenames of all external links.
    
    Parameters
    ----------
    file : str
        The name of the HDF5 file to read.

    file_mappings : dict
        A dictionary containing the old names and new names of the files.

    Returns
    -------
    None
    """
    print(f"Remapping external links in file: {file}")

    file_path = os.path.join(directory, file)

    with h5py.File(file_path, "r") as source:
        new_filename = file_mappings.get(file)
        if new_filename is None:
            print(f"No mapping found for {file}, skipping...")
            return

        new_file_path = os.path.join(directory, new_filename)
        with h5py.File(new_file_path, "w") as target:
            duplicate_hdf5(source, target)

def external_link_wrapper(directory: str, file: str, file_mappings: dict) -> None:
    """
    Given an HDF5 file, updates the external links to point to the new files.
    
    Parameters
    ----------
    file : str
        The name of the HDF5 file to read.

    file_mappings : dict
        A dictionary containing the old names and new names of the files.

    Returns
    -------
    None
    """
    print(f"Remapping external links in file: {file}")

    file_path = os.path.join(directory, file)

    with h5py.File(file_path, "r") as source:
        new_filename = file_mappings.get(file)
        if new_filename is None:
            print(f"No mapping found for {file}, skipping...")
            return

        new_file_path = os.path.join(directory, new_filename)
        with h5py.File(new_file_path, "r+") as target:
            update_external_links(source, target, file_mappings)
            

def rename_file_batch(directory: str, file_mappings: dict) -> None:
    print(file_mappings)
    files_to_update_links = []

    for file in file_mappings.keys():
        # If extension is .h5 or .nxs, update the internal metadata
        if file.endswith(".h5") or file.endswith(".nxs"):
            print(f"Duplicating file: {file} -> {file_mappings[file]}")
            try:
                # Duplicate the file and store it in the list for updating links later
                duplicate_wrapper(directory, file, file_mappings)
                files_to_update_links.append(file_mappings[file])
            except OSError as e:
                print(f"Error duplicating file: {e}")
        else:
            # For other files, simply rename
            print(f"Renaming file: {file} -> {file_mappings[file]}")
            try:
                os.rename(os.path.join(directory, file), os.path.join(directory, file_mappings[file]))
            except OSError as e:
                print(f"Error renaming file: {e}")

    # Update external links after all files have been renamed
    for file in files_to_update_links:
        print(f"Remapping external links in file: {file}")
        try:
            external_link_wrapper(directory, file, file_mappings)
        except OSError as e:
            print(f"Error remapping links: {e}")


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
        rename_file_batch(directory, file_mappings)
        print("Files renamed, links updated.")
    else:
        print("Rename cancelled. Exiting..")
