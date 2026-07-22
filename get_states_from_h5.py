import h5py
import numpy as np
import os

def get_states_from_h5(validtime,filein='/Dedicated/IFC/rush/states.h5'):
    with h5py.File(filein, 'r') as f:
        # Find the index of the requested validtime
        validtime_index = np.where(f['validtime'][:] == validtime)[0]
        if len(validtime_index) == 0:
            raise ValueError(f"Validtime {validtime} not found in the HDF5 file.")
        out = {}
        vars = ['static', 'surface', 'toplayer', 'bottomlayer', 'swe','routing_initial']
        for var in vars:
            if var not in f:
                raise ValueError(f"Variable '{var}' not found in the HDF5 file.")
            # Extract the state for the given validtime
            out[var] = f[var][:, validtime_index[0]]
    return out