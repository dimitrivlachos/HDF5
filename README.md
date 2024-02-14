# HDF5

HDF5 utilities

> To install dependencies you require mamba:
Please refer to the [mamba installation guide](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html) for instructions on how to install mamba.

Install dependencies using
`conda create --name <env> --file requirements.txt`

> **NB: No dependecies as of now**

Activate mamba virtual environment using: `mamba activate /path/to/ENV/`

# h5_rename.py

This script allows you to rename files in a directory that start with a specific prefix. It also updates the metadata of .h5 files to reflect the new filename prefix.

## Usage

1. Run the script using the following command:

    `
    python .\h5_rename.py [directory] [prefix] [new_prefix]
    `

    - `directory`: The directory to search for files.
    - `prefix`: The prefix to search for in the filenames.
    - `new_prefix`: The new prefix to rename the files to.

    Example usage:

    `
    python .\h5_rename.py data _b99 experiment1
    `

    This will find and prompt for confirmation to rename all files in the specified directory that start with `_b99` 
    
    ```bash
    Found matching files: ['_b99.run', '_b99_1.nxs', _b99_1_000001.h5', '_b99_1_header.cbf', '_b99_1_master.h5', '_b99_1_meta.h5']
    Do you want to rename these files? (y/n): 
    ````
    
    Upon confirmation, `_b99` will be replaced with `experiment1` as the new prefix. **It will also update the metadata of any .h5 files to reflect the new filename prefix**.

    > 'experiment1.run'<br>
    > 'experiment1_1.nxs'<br>
    > 'experiment1_1_000001.h5'<br>
    > 'experiment1_1_header.cbf'<br>
    > 'experiment1_1_master.h5'<br>
    > 'experiment1_1_meta.h5'<br>

    `experiment1_1_master.h5` header:
    >HDF5 "experiment1_1_master.h5" {<br>
    >&nbsp;&nbsp;&nbsp;&nbsp;
    GROUP "/" {<br>
    >&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    GROUP "entry" {<br>
    >&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    ATTRIBUTE "NX_class" {<br>
    >&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    DATATYPE  H5T_STRING {<br>
    >...

> Note: If you do not provide the directory, prefix, and new prefix as command-line arguments, the script will prompt you to enter them interactively.
