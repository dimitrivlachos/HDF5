import h5py
import sys

def search_h5_file(filename, search_string):
    # Search in filename
    if search_string in filename:
        print(f"Found '{search_string}' in filename: {filename}")

    # Search in file header
    with open(filename, 'rb') as f:
        header = f.read(80)  # HDF5 header is usually within the first 80 bytes
        header_str = header.decode('ascii', errors='ignore')
        if search_string in header_str:
            print(f"Found '{search_string}' in file header: {header_str.strip()}")

    # Search in groups and datasets
    with h5py.File(filename, 'r') as file:
        for key in file.keys():
            print(f"Key: {key}")
            if search_string in key:
                print(f"Found '{search_string}' in key: {key}")
            dataset = file[key]
            if isinstance(dataset, h5py.Dataset):
                if search_string in dataset.name:
                    print(f"Found '{search_string}' in dataset: {dataset.name}")

# Usage example
# filename = 'data/_b99_1_master.h5'
# search_string = '_b99_1_master'
# search_h5_file(filename, search_string)

if __name__ == "__main__":
    filename = sys.argv[1]
    search_string = sys.argv[2]
    search_h5_file(filename, search_string)