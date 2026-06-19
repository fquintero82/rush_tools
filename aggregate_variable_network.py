from cupyx.scipy.sparse.linalg import factorized
from scipy.sparse.linalg import factorized as factorized_sci
import cupy as cp
import numpy as np
import cupyx as cpx
#from scipy.sparse.linalg import svds
from scipy import sparse
import pandas as pd


def create_sparse_matrix_acc_basin(network=None, idx_upstream_links=None,in_scipy=False):
    """Crea la sparse matrix necesaria para el calculo de acumulacion de variables a lo largo
    de la red de drenaje

    Args:
        network (pandas.DataFrame, optional): DataFrame con la red de drenaje, como el que construye
        la funcion get_data_rvr_prm . Si es None, carga la red fina de Iowa.
        idx_upstream_links (np.array, optional): Array de  dimensiones (N,4) como el que genera la funcion get_data_rvr_prm.  
        Si es None, carga la red fina de Iowa.

    Returns:
        _type_: Matriz dispersa de dimensiones (N,N) con la topologia de la red donde N es el numero de canales. 
        Cada fila representa un canal. Las columnas con valor -1 indican el indice de los links que contribuyen aguas arriba.
    """
    if network is None and idx_upstream_links is None:
        pass
        #df, aux = get_data_rvr_prm()
    else:
        df = network
        aux = idx_upstream_links
    
    ids = df['idx'].to_list()
    N = len(ids)
    nups = df['nup'].to_list()
    data = []
    col = []
    row = []
    for i in range(0,N):
        #process leafs
        if nups[i]==0:
            data.append(1)
            col.append(i)
            row.append(i)
        if nups[i]>0:
            #the link itself
            data.append(1)
            col.append(i)
            row.append(i)
            #the upstream links
            for j in range(0,int(nups[i])):
                col_index = aux[i,j]
                data.append(-1)
                row.append(i)
                col.append(col_index)

    cpdata = cp.array(data,dtype=cp.float32)
    cprow = cp.array(row,dtype=cp.int32)
    cpcol = cp.array(col,dtype=cp.int32)
    if in_scipy:
        sparse_matrix_acc_basin = sparse.csc_matrix((data, (row,col )), shape=(N, N),dtype=np.float32)
    else:
        sparse_matrix_acc_basin = cpx.scipy.sparse.csc_matrix((cpdata, (cprow,cpcol )), shape=(N, N))
    
    return sparse_matrix_acc_basin           

def accumulate(vals,sparse_matrix_acc=None,drain_area=None,in_scipy=False):
    """Calcula la multiplicacion de matrices necesaria para acumular una variable a lo largo de la red de drenaje.

    Args:
        vals (numpy.array): Matriz de dimensiones (N,T) con la variable a agregar.  N es el numero de canales, T son los pasos de tiempo
        sparse_matrix_acc (_type_, optional): Matriz dispersa como la que genera la funcion create_sparse_matrix_acc_basin. si la matriz no es invertible se produce un error. Si es None se calclua para la red de Iowa.
        drain_area (_type_, optional): Array de dimension N con el area de drenaje de cada link. Defaults to None.

    Returns:
        _type_: _description_
    """
    if in_scipy==False:
        if sparse_matrix_acc is None:
            sparse_matrix_acc = create_sparse_matrix_acc_basin()
        try:
            solve = factorized(sparse_matrix_acc)
        except Exception as e:
            print(e)
            quit()
        out = solve(vals)
        if drain_area is not None:
            out = out / drain_area[:, np.newaxis] #broadcasting
        return out
    if in_scipy:
        if sparse_matrix_acc is None:
            sparse_matrix_acc = create_sparse_matrix_acc_basin(in_scipy=True)

        solve2 = factorized_sci(sparse_matrix_acc)
        out = solve2(vals)
        if drain_area is not None:
            out = out / drain_area[:, np.newaxis] #broadcasting
        return out


if __name__ == "__main__":
    df = pd.read_csv('southfork_rush_tiles.csv')
    idx_upstream_link = df[['up1','up2','up3','up4']].to_numpy(dtype=np.int32)
    sparse_matrix_acc = create_sparse_matrix_acc_basin(df,idx_upstream_link)
    print('sparse matrix created succesfully')
    var = np.ones((len(df),10),dtype=np.float32)
    out = accumulate(var,sparse_matrix_acc)
    print('accumulation calculated succesfully')
    
