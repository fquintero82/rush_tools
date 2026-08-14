import zarr
import numpy as np
import os
import datetime
from pathlib import Path
#from zarr.codecs.numcodecs import Delta
from datetime import timezone
 
def create_empty_file(links = None,mode='state',year=2000,path ='/Dedicated/IFC/rush'):
    #create an empty HDF5 file with the required structure to save the states

    t_start = int(datetime.datetime(year,1,1,0,tzinfo=datetime.timezone.utc).timestamp())
    t_end = int(datetime.datetime(year+1,1,1,0,tzinfo=datetime.timezone.utc).timestamp())
    t_range = np.arange(t_start, t_end,3600,dtype=np.uint32) #1970 to 2106
    nt = len(t_range)

    if links is None:
        raise ValueError("Links must be provided to create the states file.")
    n_links = len(links)
    #chunks are for read
    #shards are for write

    if mode in ['state','states']:
        vars = ['static', 'surface', 'toplayer', 'bottomlayer', 'swe','routing_initial']
        shape = (n_links,nt) 
        chunks= (n_links, 1) #only need to read one field at a time
        shards =(n_links,24) # can write 24 fields at a time
        fileout=Path(path,f'states_{year}.zarr')
    if mode in ['simulation','simulations']:
        vars = ['routing_output']
        shape = (n_links,nt)
        chunks = (1000,nt) # reads one time series for one link
        shards =(100000,nt) #writes one day for 1000 links at a time
        fileout=Path(path,f'simulations_{year}.zarr')
    if mode in ['forecast_timeseries','forecasts_timeseries']:
        vars = ['routing_output']
        shape = (n_links,nt,5*24)
        chunks = (1,1,5*24) # read forecast for 1 link , 1 issue time, five days
        shards = (1000,24,5*24) 
        fileout=Path(path,f'forecast_timeseries_{year}.zarr')
    if mode in ['forecast_maps','forecasts_maps']:
        vars = ['routing_output']
        shape = (n_links,nt,5*24)
        chunks = (n_links,1,1)
        shards = (1000,24,5*24)
        fileout=Path(path,f'forecast_maps_{year}.zarr')

    if os.path.exists(fileout):  # Check if file already exists
        return  # If it does, exit this function early
    
    
    #compressors = zarr.codecs.BloscCodec(cname='zstd', clevel=3, shuffle='bitshuffle')
    #filters = [Delta(dtype='int32')]

    #root = zarr.group(fileout)
    for var in vars:
        zarr.create_array(store=fileout,
                            name=var, 
                            shape=shape,
                            chunks=chunks,
                            shards=shards,
                            #filters = filters,
                            #compressors=compressors,
                            dtype=np.float32,
                            fill_value=np.nan)
        
    zarr.create_array(store=fileout,name='links', data = links)
    if mode in ['state','simulation','states','simulations']:
        zarr.create_array(store=fileout,name='validtime', data = t_range)  # Time dataset
    
    if mode in ('forecast_timeseries','forecast_maps','forecasts_timeseries','forecasts_maps'):
        zarr.create_array(store=fileout,name='issuetime', data = t_range)
        zarr.create_array(store=fileout,name='leadtime', data = np.arange(5*24))  # Time dataset

def _write1(states,links,validtime,p,year,mode,path):
    if not os.path.exists(p): 
        create_empty_file(links = links,mode=mode,year=year,path =path)
    z = zarr.open(p)
    print(z.tree())
    #print(validtime)

    indices = np.where(np.isin(z['validtime'], validtime))[0]
    #print(indices)
    for var in states:
        if var not in z:
            raise ValueError(f"Variable '{var}' not found in the Zarr file.")
        #print(z[var][:, indices].shape)
        #print(states[var][:].shape)
        z[var][:, indices] = states[var][:]

def write_state(states, links, validtime,path):
    year = datetime.datetime.fromtimestamp(validtime[0], tz=timezone.utc).year
    p = Path(path,f'states_{year}.zarr')
    mode='state'
    _write1(states,links,validtime,p,year,mode,path)

def write_simulation(states,links, validtime,path):
    year = datetime.datetime.fromtimestamp(validtime[0], tz=timezone.utc).year
    p = Path(path,f'simulations_{year}.zarr')
    mode='simulations'
    _write1(states,links,validtime,p,year,mode,path)

def _write2(states,links,issuetime,p,year,mode,path):
    if not os.path.exists(p): 
        create_empty_file(links = links,mode=mode,year=year,path =path)   
    z = zarr.open(p)
    indices = np.where(np.isin(z['issuetime'], issuetime))[0]
    for var in states:
        if var not in z:
            raise ValueError(f"Variable '{var}' not found in the Zarr file.")
        z[var][:, indices,0:5*24] = states[var]

def write_forecast_timeseries(states,links,issuetime,path):
    year = datetime.datetime.fromtimestamp(issuetime[0], tz=timezone.utc).year
    p = Path(path,f'forecast_timeseries_{year}.zarr')
    mode='forecast_timeseries'
    _write2(states,links,issuetime,p,year,mode,path)
    

def write_forecast_maps(states,links,issuetime,path):
    year = datetime.datetime.fromtimestamp(issuetime[0], tz=timezone.utc).year
    p = Path(path,f'forecast_maps_{year}.zarr')
    mode='forecast_timeseries'
    _write2(states,links,issuetime,p,year,mode,path)

if __name__ == '__main__':
    links = np.arange(1000000,dtype=np.uint32)
    mode='state'
    mode = 'simulation'
    mode ='forecast_timeseries'
    mode ='forecast_maps'
    year=2000
    path ='/Dedicated/IFC/rush'
    create_empty_file(links = links,mode=mode,year=year,path ='U:')
    p = Path('U:','states_2000.zarr')
    p = Path('U:','simulation_2000.zarr')
    p = Path('U:','forecast_timeseries_2000.zarr')
    z2 = zarr.open_group(p, mode='r')
    print(z2.tree())
