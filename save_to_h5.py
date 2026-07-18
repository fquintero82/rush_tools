import h5py
import numpy as np
import os

def _create_empty_states_file(links = None):
    #create an empty HDF5 file with the required structure to save the states
    if links is None:
        raise ValueError("Links must be provided to create the states file.")
    n_links = len(links)
    fileout = '/Dedicated/IFC/rush/states.h5'
    vars = ['static', 'surface', 'toplayer', 'bottomlayer', 'swe','routing_output','routing_initial']
    with h5py.File(fileout, 'w') as f:
        for var in vars:
            f.create_dataset(var, 
                            shape=(n_links,0),
                            maxshape=(n_links, None),
                            chunks=(n_links, 1),
                            compression='gzip',
                            scaleoffset=2, #scale=2 means multiply by 10^2 (keeps 2 decimal places)
                            dtype='float16')
        f.attrs['links'] = np.array(links, dtype=int)  # Store links as integers
        f.create_dataset('time', shape=(0,), maxshape=(None,), chunks=(1,), dtype='int32')  # Time dataset  

    def write_states_to_h5(states,links, time, fileout='/Dedicated/IFC/rush/states.h5'):
        """
        Writes the states to the HDF5 file. If the file does not exist, it creates it.
        """
        #states is a list of dictionaries with keys:
        #  'static', 'surface', 'toplayer', 'bottomlayer', 'swe', 'routing_output', 'routing_initial'
        

        #if fileout does not exist, create it with the required structure
        if not os.path.exists(fileout):
            _create_empty_states_file(links=links)

        with h5py.File(fileout, 'a') as f:
            #firsth check if the time already exists in the file, if so, overwrite the data for that time
            if time in f['time']:
                time_index = np.where(f['time'][:] == time)[0][0]
                for var in states:
                    if var not in f:
                        raise ValueError(f"Variable '{var}' not found in the HDF5 file.")
                    f[var][:, time_index] = states[var]
            else:
                # Append the new time value
                current_time_size = f['time'].shape[0]
                f['time'].resize((current_time_size + 1,))
                f['time'][current_time_size] = time
                
                for var in states:
                    if var not in f:
                        raise ValueError(f"Variable '{var}' not found in the HDF5 file.")
                    
                    # Resize the dataset to accommodate new data
                    current_size = f[var].shape[1]
                    f[var].resize((f[var].shape[0], current_size + 1))
                    
                    # Write the new state data
                    f[var][:, current_size] = states[var]