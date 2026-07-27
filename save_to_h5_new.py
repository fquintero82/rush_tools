import h5py
import numpy as np
import os
import datetime

def create_empty_file_states(links = None,year=2000):
    #create an empty HDF5 file with the required structure to save the states
    fileout=f'E:/Dedicated/IFC/rush/states_{year}.h5'
    if os.path.exists(fileout):  # Check if file already exists
        return  # If it does, exit this function early
    # ... rest of your code ...
 
    if links is None:
        raise ValueError("Links must be provided to create the states file.")
    n_links = len(links)


    t_start = int(datetime.datetime(year,1,1,0,tzinfo=datetime.timezone.utc).timestamp())
    t_end = int(datetime.datetime(year+1,1,1,0,tzinfo=datetime.timezone.utc).timestamp())
    t_range = np.arange(t_start, t_end,3600,dtype=np.int32)
    nt = len(t_range)

    vars = ['static', 'surface', 'toplayer', 'bottomlayer', 'swe','routing_output','routing_initial']

    with h5py.File(fileout, 'w') as f:
        f.create_dataset('links', shape=(n_links,), dtype=np.uint32, compression='gzip')

        for var in vars:
            f.create_dataset(var, 
                            shape=(n_links,nt),
                            chunks=(1000, 1),
                            compression='gzip',
                            scaleoffset=2, #scale=2 means multiply by 10^2 (keeps 2 decimal places)
                            dtype=np.float32)

        f['links'][:] = np.array(links, dtype=np.uint32)
        #valid time: the time for which data is valid
        f.create_dataset('validtime', data = t_range, chunks=(1,), dtype=np.uint32, compression='gzip')  # Time dataset
        

def write_to_h5(states,links, validtime,issuetime,writetime, mode,fileout='/Dedicated/IFC/rush/states.h5'):
    """
    Writes the states to the HDF5 file. If the file does not exist, it creates it.
    """
    #states is a list of dictionaries with keys:
    #  'static', 'surface', 'toplayer', 'bottomlayer', 'swe', 'routing_output', 'routing_initial'
    

    #if fileout does not exist, create it with the required structure
    if not os.path.exists(fileout):
        create_empty_file(links=links,mode=mode)

    with h5py.File(fileout, 'a') as f:
        # Append the new time value
        current_time_size = f['validtime'].shape[0]
        f['validtime'].resize((current_time_size + len(validtime),))
        f['validtime'][current_time_size:current_time_size + len(validtime)] = validtime

        current_time_size = f['issuetime'].shape[0]
        f['issuetime'].resize((current_time_size + len(issuetime),))
        f['issuetime'][current_time_size:current_time_size + len(issuetime)] = issuetime

        current_time_size = f['writetime'].shape[0]
        f['writetime'].resize((current_time_size + len(writetime),))
        f['writetime'][current_time_size:current_time_size + len(writetime)] = writetime
        
        for var in states:
            if var not in f:
                raise ValueError(f"Variable '{var}' not found in the HDF5 file.")
            
            # Resize the dataset to accommodate new data
            current_size = f[var].shape[1]
            f[var].resize((f[var].shape[0], current_size + len(validtime),))
            
            # Write the new state data
            print(current_size, current_size + len(validtime), states[var].shape)
            f[var][:, current_size:current_size + len(validtime)] = states[var]

if __name__=='__main__':
    links = np.arange(0,1010000,dtype=int)
    create_empty_file_states(links,year=2000)
