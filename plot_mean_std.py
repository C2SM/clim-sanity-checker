# standard modules
import os
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_pdf import PdfPages

# aliased standard modules
import numpy as np
import matplotlib.pyplot as plt

# modules of sanity checker
import paths

# standalone imports
from logger_config import log

'''
Module that contains functions to plot the results of tests. It contains:

    - plt_welchstest: plot column-bar of mean values together with all
            references, put appropiate color as background of plots

C.Siegenthaler 07.2020 (C2SM)

'''

def plt_welchstest(df_tot, new_exp, df_result, p_stages = paths.p_stages):
    '''

    :param df_tot:  Dataframe containing containing all global annual mean (reference & new_exp)
    :param new_exp:   Name of the new exp which is analysed
    :param df_result: Dataframe containing the results of the Welch's test
    :param p_stages : path to save the figures

    :return: None, but the figure is saved in p_stages
    '''

    # simple statistics, sort by exp (to be sure the order is the same in both dataframe
    df_tot_mean = df_tot.groupby(['exp']).mean().sort_values(['exp']).reset_index()
    # for std, the panda std has a bug cf https://github.com/pandas-dev/pandas/issues/16799
    df_tot_std = df_tot.groupby(['exp']).std().sort_values(['exp']).reset_index()

    # ensure new exp to be the last line
    iexp = df_tot_mean.index[df_tot_mean['exp'] == new_exp]
    new_order = df_tot_mean.index.drop(iexp).append(iexp)
    df_tot_mean = df_tot_mean.reindex(new_order)
    df_tot_std = df_tot_std.reindex(new_order)

    # number col/rows per page
    nlin = 3
    ncol = 3
    nplot = nlin * ncol

    # needed for multipage pdf file
    filename_mean_std_figures = 'glob_means_{}.pdf'.format((new_exp))
    p_pdf_file_var = os.path.join(p_stages,filename_mean_std_figures)
    pp = PdfPages(p_pdf_file_var)

    # loop over all variables
    for ivar,var in enumerate(df_result.variable):
        log.debug('Create plot for {}'.format(var))

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
        nmisval = df_tot_mean[var].isna().sum()
        i_newexp = len(xaxis)-nmisval-1
        # define colors
        colors = len(xaxis) * ['k']
        colors[i_newexp:len(xaxis)] = 'k'
        # define thickness
        thickness = len(xaxis) * [1.5]
        thickness[i_newexp] = 3

        # plot mean and std for each variable
        act_plt.errorbar(xaxis, df_tot_mean[var], yerr=df_tot_std[var],fmt='+k',ecolor = colors, elinewidth = thickness)

        # plot average reference experiments (grey band)
        m_ref = df_tot[df_tot.exp != new_exp][var].mean()
        s_ref = df_tot[df_tot.exp != new_exp][var].std()
        act_plt.axhline(m_ref, c = 'k')
        act_plt.fill_between([-1, max(xaxis)-0.5], m_ref-s_ref, m_ref+s_ref, facecolor='grey',alpha=0.6)

        # plot color background
        color_graph = df_result.loc[df_result.variable == var]['col-graph'].values[0]
        act_plt.set_facecolor('{}'.format(color_graph))

        # manage labels/titel/etc
        # -------------------------------------------------------------------------------
        # label settings
        act_plt.xaxis.set_ticks(xaxis)
        act_plt.set_xticklabels(df_tot_mean['exp'],rotation=90)

        # title settings
        pvalue = float(df_result[df_result.variable == var]['p-value'])
        act_plt.set_title('{}, p-value = {:.2%}'.format(var,pvalue))

        # Saving page & increase number var
        # --------------------------------------------------------------------------------
        # save full page
        if (iplot == (nplot - 1)):
            pp.savefig()

    # save and close odf file file
    fig.savefig(pp, format='pdf')
    pp.close()

    log.info('Detailed plots of mean and standard deviation per variable can be found in the file {}'.format(p_pdf_file_var))

