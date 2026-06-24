import numpy as np

def calib_with_constrains2(evaluation,sf,interf,bf,discharge,maxbf=None):
    
    simulation = sf + interf + bf
    #simulation = discharge


    if len(evaluation) != len(simulation):
        return np.nan
    '''Maximum Surface Flow ($y_1$): Surface flow often has a faster, higher peak.
     Its maximum bound might be tied to the maximum observed flow rate
      or a fraction of the maximum observed precipitation.
      Example: $y_{1,i} \le \text{Max Flow Obs}$'''
#    if sf>np.max(evaluation).any():
#        return np.nan
    #if total volume of simulation is less than 90% of observation, ignore the simulation
    if np.sum(simulation) < 0.9*np.sum(evaluation):
        return 1e3
    #if baseflow is more than 30% of the total simulation, ignore simulation
    if np.sum(bf) > 0.30*np.sum(simulation):
        return 1e3
    #if baseflow is less than 10% of total runoff, ignore simulation
    if np.sum(bf) < 0.1*np.sum(simulation):
        return 1e3
    if max_bf is not None:
        if np.max(bf)>max_bf:
            return 1e3
    #if surface flow is more than 20% of total runoff, ignore simulation
    if np.sum(sf) > 0.2*np.sum(simulation):
        return 1e3
        
    
    
    obs, sim = np.array(evaluation), np.array(simulation)
    corr = np.corrcoef(obs,sim)[0,1]
    return 1. - float(corr)
    #bias = np.nansum(obs - sim) / len(obs)
    #return float(bias)

def calib_with_constrains1(evaluation,sf,interf,bf):
    
    simulation = sf + interf + bf
    if len(evaluation) != len(simulation):

        return np.nan

    #if total volume of simulation is less than 90% of observation, ignore the simulation
    if np.sum(simulation) < 0.9*np.sum(evaluation):
        return 1e3
    #if baseflow is more than 30% of the total simulation, ignore simulation
    if np.sum(bf) > 0.30*np.sum(simulation):
        return 1e3
    #if baseflow is less than 10% of total runoff, ignore simulation
    if np.sum(bf) < 0.1*np.sum(simulation):
        return 1e3
    #if surface flow is more than 20% of total runoff, ignore simulation
    if np.sum(sf) > 0.2*np.sum(simulation):
        return 1e3
        
    
    
    obs, sim = np.array(evaluation), np.array(simulation)
    #corr = np.corrcoef(obs,sim)[0,1]
    #return 1. - float(corr)
    bias = np.nansum(obs - sim) / len(obs)
    return float(bias)

def fdc_signature_error(sim, obs):
    # Sort both descending
    sort_sim = np.sort(sim)[::-1]
    sort_obs = np.sort(obs)[::-1]
    
    # Calculate the Mean Absolute Error between the sorted curves
    # This ignores timing and only looks at the distribution of magnitudes
    return np.mean(np.abs(sort_sim - sort_obs))

def calib_with_constrains_fdc(evaluation,sf,interf,td,bf,maxbf=None):
    
    simulation = sf + interf + td + bf
    #simulation = discharge

    if len(evaluation) != len(simulation):
        return np.nan
    error=0
    add = 1
#    if sf>np.max(evaluation).any():
#        return np.nan
    #if total volume of simulation is less than 90% of observation, ignore the simulation
    if np.sum(simulation) < 0.9*np.sum(evaluation):
        error+=add
        #return 1e3
    #if baseflow is more than 30% of the total simulation, ignore simulation
    if np.sum(bf) > 0.30*np.sum(evaluation):
        error+=add
        #return 1e3
    #if baseflow is less than 10% of total runoff, ignore simulation
    if np.sum(bf) < 0.1*np.sum(evaluation):
        error+=add
        #return 1e3
    # if maxbf is not None:
    #     if np.max(bf)>maxbf:
    #         error+=add
            #return 1e3
    #if surface flow is more than 60% of total runoff, ignore simulation
    if np.sum(sf) > 0.3*np.sum(evaluation):
        error+=add
        #return 1e3
    #if interflow is more than 50% of total runoff, ignore simulation
    if np.sum(interf) > 0.3*np.sum(evaluation):
        error+=add
        #return 1e3
    #if tiledrainage is more than 30% of the total simulation, ignore simulation
    if np.sum(td) > 0.30*np.sum(evaluation):
        error+=add
        #return 1e3
    #if maximum of simulation is larger than observed, penalize
    if max(simulation) > max(evaluation):
        error+=add*5
        #return 1e3
    
    
    obs, sim = np.array(evaluation), np.array(simulation)
    #corr = np.corrcoef(obs,sim)[0,1]
    fdc = fdc_signature_error(sim,obs) #0 if low
    error+=fdc
    return error
    #return 1. - float(corr)
    #bias = np.nansum(obs - sim) / len(obs)
    #return float(bias)

def calib_with_constrains_mae(evaluation,sf,interf,td,bf,maxbf=None):
    
    simulation = sf + interf + td + bf
    #simulation = discharge

    if len(evaluation) != len(simulation):
        return np.nan
    error=0
    add = 1
#    if sf>np.max(evaluation).any():
#        return np.nan
    #if total volume of simulation is less than 90% of observation, ignore the simulation
    if np.sum(simulation) < 0.9*np.sum(evaluation):
        error+=add
        #return 1e3
    #if baseflow is more than 30% of the total simulation, ignore simulation
    if np.sum(bf) > 0.30*np.sum(evaluation):
        error+=add
        #return 1e3
    #if baseflow is less than 10% of total runoff, ignore simulation
    if np.sum(bf) < 0.1*np.sum(evaluation):
        error+=add
        #return 1e3
    # if maxbf is not None:
    #     if np.max(bf)>maxbf:
    #         error+=add
            #return 1e3
    #if surface flow is more than 60% of total runoff, ignore simulation
    if np.sum(sf) > 0.3*np.sum(evaluation):
        error+=add
        #return 1e3
    #if interflow is more than 50% of total runoff, ignore simulation
    if np.sum(interf) > 0.3*np.sum(evaluation):
        error+=add
        #return 1e3
    #if tiledrainage is more than 30% of the total simulation, ignore simulation
    if np.sum(td) > 0.30*np.sum(evaluation):
        error+=add
        #return 1e3
    #if maximum of simulation is larger than observed, penalize
    if max(simulation) > max(evaluation):
        error+=add*5
        #return 1e3
    
    
    obs, sim = np.array(evaluation), np.array(simulation)
    #corr = np.corrcoef(obs,sim)[0,1]
    mae = sum(abs(sim -obs))/len(obs) #0 if low
    error+=mae
    return error
    #return 1. - float(corr)
    #bias = np.nansum(obs - sim) / len(obs)
    #return float(bias)

def calib_mae(evaluation,sf,interf,td,bf,maxbf=None):
    
    simulation = sf + interf + td + bf
    #simulation = discharge

    if len(evaluation) != len(simulation):
        return np.nan
    error=0
    
    obs, sim = np.array(evaluation), np.array(simulation)
    #corr = np.corrcoef(obs,sim)[0,1]
    mae = sum(abs(sim -obs))/len(obs) #0 if low
    error+=mae
    return error
    #return 1. - float(corr)
    #bias = np.nansum(obs - sim) / len(obs)
    #return float(bias)

def calib_with_constrains4(evaluation,sf,interf,td,bf,maxbf=None):
    
    simulation = sf + interf + td + bf
    #simulation = discharge

    if len(evaluation) != len(simulation):
        return np.nan

    obs, sim = np.array(evaluation), np.array(simulation)
    error = fdc_signature_error(sim,obs)
    return error

def calib_with_constrains5(evaluation,simulation):
    

    if len(evaluation) != len(simulation):
        print("evaluation and simulation lists does not have the same length.")
        return np.nan

    obs, sim = np.array(evaluation), np.array(simulation)
    error = 1- np.corrcoef(obs,sim)[0,1]
    return error

def get_csi(obs,fcst,threshold):
    # Binarize the arrays based on the threshold (True/False)
    obs_event = obs >= threshold
    fcst_event = fcst >= threshold
    
    # Calculate components of the contingency table
    hits = np.sum(obs_event & fcst_event)
    false_alarms = np.sum((~obs_event) & fcst_event)
    misses = np.sum(obs_event & (~fcst_event))
    
    # Calculate denominator
    denominator = hits + false_alarms + misses
    
    # Handle the edge case where no events were observed or forecasted
    if denominator == 0:
        return np.nan
        
    csi = hits / denominator
    return csi

def calib_corr_csi(evaluation,simulation,fl):

    if len(evaluation) != len(simulation):
        print("evaluation and simulation lists does not have the same length.")
        return np.nan
    error=0
    obs, sim = np.array(evaluation), np.array(simulation)
    corr = 1- np.corrcoef(obs,sim)[0,1]
    error+=corr
    csi = get_csi(evaluation,simulation,fl)
    error+= 1-csi
    return error
