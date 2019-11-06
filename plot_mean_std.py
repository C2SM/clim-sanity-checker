
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use('Agg') #for saving plot
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages  # multiple pages in pdf

def plt_var(df_ref,df_new_exp,new_exp):


    # simple statistics
    df_ref_mean = df_ref.groupby(['exp'], as_index=False).mean()
    # for std, the panda std has a bug cf https://github.com/pandas-dev/pandas/issues/16799
    df_ref_std = df_ref.groupby(['exp']).std().reset_index()

    # to be sure all the exps are in the same order
    df_ref_mean.sort_values(by=['exp'],inplace=True)
    df_ref_std.sort_values(by=['exp'],inplace=True)

    # compute same statistics on df_new_exp and include them in df_tot (new tot dataframe)
    dict_new_exp_mean = dict(df_new_exp.mean())
    dict_new_exp_mean['exp'] = new_exp
    df_tot_mean = df_ref_mean.append(dict_new_exp_mean,ignore_index=True)
    dict_new_exp_std = dict(df_new_exp.std())
    dict_new_exp_std['exp'] = new_exp
    df_tot_std = df_ref_std.append(dict_new_exp_std, ignore_index=True)

    # number col/rows per page
    nlin = 3
    ncol = 3
    nplot = nlin * ncol

    # needed for multipage pdf file
    pp = PdfPages('plots_variables.pdf')

    # needed to count on which plot we are
    ivar = 0

    # loop over all variables
    for var in df_new_exp.keys():
        if 'exp' in var:
            continue

        # subplot preparation
        # ------------------------------------------------------------------------
        # number of plot
        iplot = np.mod(ivar,nplot)

        # set the plotting frame
        if (iplot == 0) :
           fig, plt_nbr = plt.subplots(nlin, ncol, sharex='col', figsize=(12, 12))

        # subplot coordinate
        icol = np.mod(iplot, ncol)
        ilin = np.int(np.floor(iplot / ncol))

        # actual plot
        act_plt = plt_nbr[ilin, icol]

        # x-axis
        xaxis = np.arange(df_tot_mean.shape[0])

        # plotting
        # ---------------------------------------------------------------------------
        # define colors
        colors = len(xaxis) * ['b']
        nmisval = df_tot_mean[var].isna().sum()
        colors[len(xaxis)-nmisval-1:len(xaxis)] = 'r'

        # plot mean and std for each variable
        act_plt.errorbar(xaxis, df_tot_mean[var], yerr=df_tot_std[var],fmt='+',ecolor = colors)

        # plot average reference experiments (green band)
        m_ref = df_ref[var].mean()
        s_ref = df_ref[var].std()
        act_plt.axhline(m_ref, c = 'green')
        act_plt.fill_between([-1, max(xaxis)+1], m_ref-s_ref, m_ref+s_ref, facecolor='green',alpha=0.4)

        # manage labels/titel/etc
        # -------------------------------------------------------------------------------
        # label settings
        act_plt.xaxis.set_ticks(xaxis)
        act_plt.set_xticklabels(df_tot_mean['exp'],rotation=90)

        # title settings
        act_plt.set_title(var)

        # Saving page & increase number var
        # --------------------------------------------------------------------------------
        # save full page
        if (iplot == (nplot - 1)):
            pp.savefig()

        ivar = ivar + 1

    # save and close odf file file
    fig.savefig(pp, format='pdf')
    pp.close()

