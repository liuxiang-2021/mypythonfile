import pandas as pd
import math
import matplotlib.pyplot as plt




if __name__ == "__main__":
    csvfile = "temps_and_workmode_128v45.csv"

    # fig = plt.figure()
    # ax=fig.add_subplot

    csv_data = pd.read_csv(csvfile)
    csv_df = pd.DataFrame(csv_data)
    # print(csv_df)
    col_list = [col for col in csv_df.columns]
    print(csv_df[col_list[1]])
    # csv_df.plot()
    # plt.show()


    # plt.clf()
    fig = plt.figure(1)
    ax1 = fig.add_subplot(2,1,1)
    ax1.plot(range(len(csv_df[col_list[1]].values)), csv_df[col_list[1]].values, label=col_list[1])
    ax1.set_xlabel('time[tick];tick=5s')
    ax1.set_ylabel('temperature[℃]')
    ax2 = ax1.twinx()
    ax2.plot(range(len(csv_df[col_list[1]].values)), csv_df[col_list[5]].values, 'r', label=col_list[5])
    plt.grid()
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    plt.legend(handles1 + handles2, labels1 + labels2, loc='upper right')

    ax3 = fig.add_subplot(2,1,1)
    ax3.plot(range(len(csv_df[col_list[1]].values)), csv_df[col_list[2]].values, label=col_list[2])
    ax3.set_xlabel('time[tick];tick=5s')
    ax3.set_ylabel('temperature[degree]')
    ax4 = ax3.twinx()
    ax4.plot(range(len(csv_df[col_list[1]].values)), csv_df[col_list[5]].values, 'r-', label=col_list[5])
    plt.grid()
    handles3, labels3 = ax3.get_legend_handles_labels()
    handles4, labels4 = ax4.get_legend_handles_labels()
    plt.legend(handles3 + handles4, labels3 + labels4, loc='upper right')
    plt.savefig('./fig1.png')
    # plt.show()

    # --------------figure 2 ------------------
    # fig = plt.figure(2)
    ax1 = fig.add_subplot(2,1,1)
    ax1.plot(range(len(csv_df[col_list[1]].values)), csv_df[col_list[3]].values, label=col_list[3])
    ax1.set_xlabel('time[tick];tick=5s')
    ax1.set_ylabel('temperature[degree]')
    ax2 = ax1.twinx()
    ax2.plot(range(len(csv_df[col_list[1]].values)), csv_df[col_list[5]].values, 'r', label=col_list[5])
    plt.grid()
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    plt.legend(handles1 + handles2, labels1 + labels2, loc='upper right')

    ax3 = fig.add_subplot(2,1,1)
    ax3.plot(range(len(csv_df[col_list[1]].values)), csv_df[col_list[4]].values, label=col_list[4])
    ax3.set_xlabel('time[tick];tick=5s')
    ax3.set_ylabel('temperature[℃]')
    ax4 = ax3.twinx()
    ax4.plot(range(len(csv_df[col_list[1]].values)), csv_df[col_list[5]].values, 'r-', label=col_list[5])
    plt.grid()
    handles3, labels3 = ax3.get_legend_handles_labels()
    handles4, labels4 = ax4.get_legend_handles_labels()
    plt.legend(handles3 + handles4, labels3 + labels4, loc='upper right')
    plt.savefig('./fig2.png')
    plt.show()


