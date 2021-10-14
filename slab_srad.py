import sys
import matplotlib.pyplot as plt

from base import *
from utils import force_stress_integration, moment_stress_integration

"""
print(f"Arguments count: {len(sys.argv)}")
for i, arg in enumerate(sys.argv):
    print(f"Argument {i:>6}: {arg}")
"""

# SETUP
folder = FOLDER_PATH
filename = 'R__SlabSec_SRAD_MPa.txt'

loadsteps = LOADSTEPS
loc_colnames = ["node", "x", "y", "z"]
x = -3
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

    res = results_in_loc(res, x=x)
    
    is_data_loaded(res)

    if plot:
        plotres = pd.DataFrame()
        plotres['smax'] = res[res_colnames].loc[res[res_colnames[-1]].idxmax()]
        plotres['smin'] = res[res_colnames].loc[res[res_colnames[-1]].idxmin()]
        
        plotres['h'] = abs(res['y'].loc[res[res_colnames[-1]].idxmax()] - res['y'].loc[res[res_colnames[-1]].idxmin()])

        tup = (
            plotres['h'].tolist(), 
            plotres['smax'].tolist(), 
            plotres['smin'].tolist()
        )
        plotres['axial_force'] = [
            force_stress_integration(y=[smax, smin], x=[-h/2, h/2]) * 1e3 
            for h, smax, smin in zip(*tup)]
        plotres['bending'] = [
            -moment_stress_integration(y=[smax, smin], x=[-h/2, h/2]) * 1e3 
            for h, smax, smin in zip(*tup)]
        
        print(plotres)
        fig, axes = plt.subplots(nrows=2)
        plotres.plot(y=['smax', 'smin'], ax=axes[0])
        plt.grid(axis="y", color="darkgray", linestyle="--")    
        axes[0].set_ylabel("Force [kN]")
        
        plotres.plot(y=['bending'], ax=axes[1])
        plt.grid(axis="y", color="darkgray", linestyle="--")    
        plt.xlabel("Loadcase")
        axes[1].set_ylabel('Bending [kNm]')
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