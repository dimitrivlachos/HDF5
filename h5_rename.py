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

import h5py
import os

def find_files_with_prefix(directory, prefix):
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
    matching_files = []
    try:
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.name.startswith(prefix):
                    matching_files.append(entry.name)
    except OSError as e:
        print(f"Error: {e}")
    return matching_files

def rename_files(directory, prefix, new_prefix, matching_files=None):
    """
    Rename files in a directory that start with a specific prefix.

    Parameters
    ----------
    directory : str
        The directory to search for files.

    prefix : str
        The prefix to search for.

    new_prefix : str
        The new prefix to rename the files to.

    Returns
    -------

    None
    """
    if matching_files is None:  # If matching_files is not provided
        matching_files = find_files_with_prefix(directory, prefix)

    for filename in matching_files:  # Loop through the files
        try:
            new_filename = filename.replace(prefix, new_prefix)
            os.rename(  # Rename the file
                os.path.join(directory, filename),  # Old filename
                os.path.join(directory, new_filename)  # New filename
            )
            print(f"Renamed {filename} to {new_filename}")

            if filename.endswith('.h5'):  # If the file is an .h5 file
                print(f"Updating metadata for {new_filename}")
                update_h5_metadata(directory, new_prefix, new_filename)
        except OSError as e:
            print(f"Error renaming {filename}: {e}")

def update_h5_metadata(directory, filename, new_filename):
    """
    Update the metadata of an .h5 file to reflect the new filename prefix.

    Parameters
    ----------
    directory : str
        The directory where the .h5 file is located.

    filename : str
        The filename of the .h5 file to update.

    new_filename : str
        The new filename to update the .h5 file to.

    Returns
    -------

    None
    """

    try:
        filename = os.path.join(directory, new_filename)

        with open(filename, 'rb') as f:  # Open the file
            header = f.read(80)  # HDF5 header is usually within the first 80 bytes
            header_str = header.decode('ascii', errors='ignore')

            if filename in header_str:
                print(f"Found '{filename}' in file header: {header_str.strip()}")
                # Update the header with the new filename prefix
                header_str = header_str.replace(filename, new_filename)
                with open(filename, 'wb') as f:
                    f.write(header_str.encode('ascii', errors='ignore'))
                    print(f"Updated file header to: {header_str.strip()}")
    except (OSError, IOError) as e:
        print(f"Error updating metadata for {new_filename}: {e}")

if __name__ == "__main__":
    import sys

    # Check if directory, prefix, and new prefix were provided as arguments
    if len(sys.argv) < 4:
        # Ask for directory, prefix, and new prefix
        directory = input("Enter the directory: ")
        prefix = input("Enter the prefix: ")
        new_prefix = input("Enter the new prefix: ")
    else:
        # Use the provided arguments
        directory = sys.argv[1]
        prefix = sys.argv[2]
        new_prefix = sys.argv[3]

    matching_files = find_files_with_prefix(directory, prefix)

    # Print the matching files and ask for confirmation
    print(f"Found matching files: {matching_files}")
    confirm = input("Do you want to rename these files? (y/n): ")
    if confirm.lower() != 'y':
        print("Rename cancelled. Exiting..")
        sys.exit(0)

    # Call the rename_files function
    rename_files(directory, prefix, new_prefix, matching_files=matching_files)
