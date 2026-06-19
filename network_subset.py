import pandas as pd

import numpy as np
import sys

def _get_basin_ids(idx:np.int32,
                    idx_upstream_links:np.ndarray,
                    link_ids:np.ndarray,
                    list_ids:list,
                    list_links:list):
    #add the id to the list                
    list_ids.append(idx)
    #add the linkid to the list
    try:
        list_links.append(link_ids[idx])
    except IndexError as e:
        print(e)
        print(idx)
    #find the id of the upstream channels
    myidx_upstream_links = idx_upstream_links[idx,]
    #check that the list is not empty
    if (myidx_upstream_links!=0).any():
        #loop through the upstream ids
        for new_idx in myidx_upstream_links[myidx_upstream_links!=0]:
            #apply the same function to the ids (recursive)
            _get_basin_ids(new_idx,
                            idx_upstream_links,
                            link_ids,
                            list_ids,
                            list_links)

def get_basin_ids(idx_outlet:np.int32,
                    link_outlet:np.int32,
                    idx_upstream_links:np.ndarray,
                    link_ids:np.ndarray):
    list_ids = []
    list_links = []
    sys.setrecursionlimit(int(1E6))
    #apply the function to the outlet recursively
    _get_basin_ids(idx_outlet,
                    idx_upstream_links,
                    link_ids,
                    list_ids,
                    list_links)
    
    sys.setrecursionlimit(int(1E3))                    
    #when the recursion stack is complete, return the list with the ids and the linkids
    return list_ids, list_links

def get_id_outlet(network:pd.DataFrame,link_outlet:int):
    #link_ids = network['link_id'].to_numpy()
    link_ids = network['links'].to_numpy()
    #find the index where the netowrk link_id is the outlet
    wh = np.where(link_ids==link_outlet)[0][0]
    
    idxs = network['idx'].to_numpy()
    id_outlet = idxs[wh]
    return id_outlet

def network_subset(network:pd.DataFrame,idx_upstream_links:np.ndarray,link_outlet:int)->pd.DataFrame:
    
    #link_ids = network['link_id'].to_numpy()
    id_outlet = get_id_outlet(network,link_outlet)
    #link_ids = network['link_id'].to_numpy()
    link_ids = network['links'].to_numpy()
    basin_ids, basin_links = get_basin_ids(id_outlet,
                        link_outlet,
                        idx_upstream_links,
                        link_ids)
    
    #subset the dataset to only new links
    #get the subset in the same order of the basin_ids
    network = network.iloc[basin_ids] 
    #assign new ids
    network['idx']= np.arange(len(network))

    idx_upstream_links = reindex_upstream_links(idx_upstream_links,basin_ids,network)
    return network,idx_upstream_links

def reindex_upstream_links(idx_upstream_links:np.ndarray,
                            basin_ids:np.ndarray,
                            network:pd.DataFrame):

    #subset upstream links
    idx_upstream_links = idx_upstream_links[basin_ids,:]
    #idx_upstream_links_new = idx_upstream_links.copy()
    #reassign new upstream link ids
    # i will use the pandas index to help
    nrow = idx_upstream_links.shape[0]
    nup = network['nup'].to_numpy()
    for i in range(0,nrow):
        #item = idx_upstream_links_new[i]
        n1 = nup[i]
        if (n1>0):
            for j in range(0,n1):
                val = idx_upstream_links[i,j]
                newval = network.loc[val,'idx']
                idx_upstream_links[i,j] = newval
    return idx_upstream_links


if __name__=='__main__':
    pass

