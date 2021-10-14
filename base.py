import os, re
import pandas as pd


#FOLDER_PATH = 'C:\\_CURRENT\\'
FOLDER_PATH = 'C:\\_CURRENT\\loading MPC flexible - tw_h 100m'
#FOLDER_PATH = 'D:\\STUDIES\\202009 Tower Height-Foundation Stiffness\\rock adapter\\Mxy 157MNm\\loading MPC flexible - tw_h 1m'
LOADSTEPS = 11


def read_txt(folder, filename, colnames):
    print(os.path.isfile(folder + os.sep + filename))
    return pd.read_csv(folder + os.sep + filename, names=colnames, delim_whitespace=True)


def is_data_loaded(df: pd.DataFrame = None, verbose: bool = True):
    if df is None:
        raise ValueError("There is no data.")

    if verbose:
        print(df)


def loop_through_folders(filename: str, colnames: list = None, path: str = None, 
    folders: list = None, folder_common_string: str = None):
    
    if not path and not folders:
        raise ValueError("One of 'path' and 'folders' must be declared")

    if path:
        folders = [f for f in os.listdir(path) if os.path.isdir(path + os.sep + f)]
    
    if not path:
        path = ''

    if folder_common_string:
        folders = [f for f in folders if folder_common_string in f.replace('-', ' ').split()]

    dfs = [read_txt(path + os.sep + f + os.sep, filename, colnames) for f in folders]
    return dfs, folders


def remove_rows_with_zeros(df: pd.DataFrame, cols: list):
    return df[df[cols].values.sum(axis=1) != 0]


def multiply_columns(df: pd.DataFrame, cols: list, factor: float):
    df[cols] = df[cols].multiply(factor, axis=1, fill_value=0)
    return df


def results_in_loc(df: pd.DataFrame, x: float = None, y: float = None, z: float = None):
    query = []
    if x:
        query += [f'x == {x}']
    if y:
        query += [f'y == {y}']
    if z:
        query += [f'z == {z}']
    
    return df.query(' & '.join(query)) if query else df


def results_max(df: pd.DataFrame, col: list = None):
    if not col:
        col = df.columns[-1]
    return df[df[col] == df[col].max()]


def results_min(df: pd.DataFrame, col: list = None):
    if not col:
        col = df.columns[-1]
    return df[df[col] == df[col].min()]


def models_summary(dfs: list, ids: list, col: str = None, col_function: str = 'max',
    x: float = None, y: float = None, z: float = None):

    if all(a == None for a in [col, x, y, z]):
        raise ValueError("'col' or a location argument ('x', 'y', 'z') must be defined")

    if col:
        if col_function == "max":
            res = pd.concat([results_max(df, col).head(1) for df in dfs])
        elif col_function == "min":
            res = pd.concat([results_min(df, col).head(1) for df in dfs])
    else:
        res = pd.concat([results_in_loc(df, x, y, z).head(1) for df in dfs])

    res = pd.concat([res.reset_index(drop=True), pd.DataFrame(ids, columns=['info'])], axis=1)
    #res = res.set_index('ids')
    return res    


def str_extract(df, col, number=False, word_list=[]):
    if number:
        return df[col].str.extract('(\d+)').astype(float)
    
    elif word_list:
        regex = '({})'.format('|'.join(word_list), flags=re.IGNORECASE, expand=False)
        return df[col].str.extract(regex)[0].str.lower().fillna('')
    
    else:
        return None


if __name__ == "__main__":

    # SETUP
    folder = 'C:\\z08\\'
    filename = 'R__FlangeBot_UY_mm.txt'
    filename = 'R__TowerBolts_Forces.txt'
    filename = 'R__SlabSec_SRAD_MPa.txt'

    loadsteps = 11

    loc_colnames = ["node", "x", "y", "z"]
    #loc_colnames = ["node", "x", "y"]
    res_colnames = [f'v{i}' for i in range(1, loadsteps+1)]
    colnames = loc_colnames + res_colnames
    

    # READ A SINGLE FILE
    #df = read_txt(folder, filename, colnames)
    #print(df)


    # READ FILES FROM A LIST OF FOLDERS
    folder = 'D:\\STUDIES\\202009 Tower Height-Foundation Stiffness\\shallow foundation\\_prev'
    folder = 'C:\\_CURRENT'
    fcstring = None#'20m'
    #print(folder.split('\\', '_'))
    dfs, folders = loop_through_folders(filename, colnames, path=folder, folder_common_string=fcstring)
    df = dfs[0]


    # EXTRACT RESULTS
    #print(results_in_loc(dfs[0], x=1.9775))
    #print(results_in_loc(dfs[0], y=0.0, x=1.813))

    #print(results_max(df))
    #print(results_min(df))

    #res = models_summary(dfs, folders, col='v7', col_function='max')
    #res = models_summary(dfs, folders, col='v11', col_function='min')
    res = models_summary(dfs, folders, x=-3, y=-2.75)
    res['tw_h'] = str_extract(res, 'info', number=True)
    word_list = ['rigid', 'flexible']
    res['mpc'] = str_extract(res, 'info', word_list=['rigid', 'flexible'])
    res = res[['mpc', 'tw_h', 'v11']].sort_values(['mpc', 'tw_h'], ascending=[True, True])
    print(res)