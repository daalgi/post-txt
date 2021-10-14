import sys
import matplotlib.pyplot as plt
from base import *

"""
print(f"Arguments count: {len(sys.argv)}")
for i, arg in enumerate(sys.argv):
    print(f"Argument {i:>6}: {arg}")
"""

# SETUP
folder = FOLDER_PATH
filename = 'R__TowerBolts_Forces.txt'

loadsteps = LOADSTEPS
loc_colnames = ["node", "x", "y"]
res_colnames = [f'lc{i}' for i in range(1, loadsteps+1)]
colnames = loc_colnames + res_colnames

# For multiple models analyses
params = ['mpc', 'tw_h']
types = ['str', 'number']
word_list = ['rigid', 'flexible']


# COMMAND LINE PASSED ARGUMENTS
opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]

single_model = True if any(o in opts for o in ['-s', '-single']) else False
multiple_model = True if any(o in opts for o in ['-m', '-multiple']) else False
plot = True if any(o in opts for o in ['-p', '-plot']) else False
to_excel = True if any(o in opts for o in ['-e', '-excel']) else False


# RESULTS
res = None

if single_model:

    # READ A SINGLE FILE
    print(folder + os.sep + filename)
    res = read_txt(folder, filename, colnames)
    res = remove_rows_with_zeros(res, res_colnames)
    res = multiply_columns(res, res_colnames, factor=1e3)
    
    is_data_loaded(res)

    if plot:
        minmax = pd.DataFrame()
        minmax['max'] = res[res_colnames].loc[res[res_colnames[-1]].idxmax()]
        minmax['min'] = res[res_colnames].loc[res[res_colnames[-1]].idxmin()]
        print(minmax)
        minmax.plot.bar()
        plt.grid(axis="y", color="darkgray", linestyle="--")    
        plt.ylabel("Force [kN]")
        plt.xlabel("Loadcase")
        plt.xticks(rotation=0)
        plt.show()


elif multiple_model:

    # READ MULTIPLE FILES FROM A LIST OF FOLDERS
    fcstring = None#'20m'
    dfs, folders = loop_through_folders(filename, colnames, path=folder, folder_common_string=fcstring)
    print('List of folders:')
    for f in folders:
        print(f)

    res = models_summary(dfs, folders, col=res_colnames[-1], col_function="max")
    
    for p, t in zip(params, types):
        if t == 'number':
            res[p] = str_extract(res, 'info', number=True)
        elif t == 'str':
            res[p] = str_extract(res, 'info', word_list=word_list)

    cols = params + [res_colnames[-1]]
    res = res[cols].sort_values(params, ascending=[True] * len(params))
    res[res_colnames[-1]] *= 1e3
    
    is_data_loaded(res)

    if plot:
        res.pivot(index="tw_h", columns="mpc", values=res_colnames[-1]).plot()
        plt.grid(axis="both", color="darkgray", linestyle="--")    
        plt.ylabel("Force [kN]")
        plt.xlabel("Modelled tower wall height [m]")
        plt.ylim(0, max(res[res_colnames[-1]])*1.1)
        plt.show()