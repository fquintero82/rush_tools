import zarr
import numpy as np
import os
import datetime
from pathlib import Path
#from zarr.codecs.numcodecs import Delta
from datetime import timezone

def get_states_from_zarr(validtime,path='/Dedicated/IFC/rush/'):
    year = datetime.datetime.fromtimestamp(validtime, tz=timezone.utc).year
    p = Path(path,f'states_{year}.zarr')
    z = zarr.open(p)
    # Find the index of the requested validtime
    validtime_index = np.where(z['validtime'][:] == validtime)[0]
    if len(validtime_index) == 0:
        raise ValueError(f"Validtime {validtime} not found in the ZARR file.")
    out = {}
    vars = ['static', 'surface', 'toplayer', 'bottomlayer', 'swe','routing_initial']
    for var in vars:
        if var not in z:
            raise ValueError(f"Variable '{var}' not found in the ZARR file.")
        # Extract the state for the given validtime
        out[var] = z[var][:, validtime_index]
    return out