""" Gantt chart """

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def make_gantt(data: pd.DataFrame, date_column: str, task_column: str):
    proj_start = data[date_column].min()
    
    task_starts = data[[task_column, date_column]].groupby(task_column).min().reset_index(drop=False)
    task_starts = task_starts.rename(columns={date_column: 'start'})
    task_ends = data[[task_column, date_column]].groupby(task_column).max()
    task_ends = task_ends.rename(columns={date_column: 'end'})
    task_summary = task_starts.join(task_ends, on=task_column)
    
    task_summary['start_num'] = (task_summary['start']-proj_start).dt.days
    task_summary['end_num'] = (task_summary['end']-proj_start).dt.days
    # days between start and end of each task
    task_summary['days_start_to_end'] = task_summary.end_num - task_summary.start_num

    fig, ax = plt.subplots(1, figsize=(16,16))
    ax.barh(task_summary[task_column], task_summary.days_start_to_end, left=task_summary.start_num)

    ##### TICKS #####
    xticks = np.arange(0, task_summary.end_num.max()+1, 365*5)
    xticks_labels = pd.date_range(proj_start, end=task_summary['end'].max()).strftime("%Y")
    xticks_minor = np.arange(0, task_summary.end_num.max()+1, 365)
    ax.set_xticks(xticks)
    ax.set_xticks(xticks_minor, minor=True)
    ax.set_xticklabels(xticks_labels[::365*5])
    return fig 