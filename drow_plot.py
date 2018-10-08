import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#1.画出IC的时间折线图和IC均值
def IC_PLOT(DATA_PATH):
    IC_data=pd.read_pickle(DATA_PATH)
    IC_data=IC_data.assign(IC_mean=np.mean(IC_data.RankIC.values))
    dates=IC_data.index.values
    plt.plot(IC_data)
    plt.xlim(dates[0],dates[-1])
    plt.xlabel('Datetime')
    plt.ylabel('RankIC')
    plt.title('Factor IC Timeseries Curve')
    plt.grid(True)
    plt.show()
    print(IC_data.head())

IC_PATH='Inter_Data/Rate5_IC.pickle'
IC_PLOT(IC_PATH)

#2.画出BETA的时间折线图和BETA均值
def BETA_PLOT(DATA_PATH):
    BETA_data=pd.read_pickle(DATA_PATH)
    BETA_data=BETA_data.loc[:,['BETA']]
    BETA_data=BETA_data.assign(BETA_MEAN=np.mean(BETA_data.BETA.values))
    dates=BETA_data.index.values
    plt.plot(BETA_data)
    plt.xlim(dates[0],dates[-1])
    plt.xlabel('Datetime')
    plt.ylabel('BETA')
    plt.title('Factor Return Timeseries Curve')
    plt.grid(True)
    plt.show()
    print(BETA_data.head())

BETA_PATH='Inter_Data/Rate5_BETA.pickle'
BETA_PLOT(BETA_PATH)

#3.画出申万一级行业分类的IC值的均值
def INDU_IC_PLOT(DATA_PATH):
    INDU_data=pd.read_pickle(DATA_PATH)
    plt.rcParams["font.sans-serif"] = ["SimHei"] #显示中文字体
    plt.rcParams['axes.unicode_minus'] = False  #显示负号
    plt.bar(INDU_data.index.values,INDU_data.IC_Mean.values)
    plt.xlabel('Industry')
    plt.ylabel('IC_Mean')
    plt.title('Industry IC Mean Value')
    plt.show()
    print(INDU_data.head())

INDU_IC_PATH='Inter_Data/indu_IC_mean.pickle'
INDU_IC_PLOT(INDU_IC_PATH)

#4.画出10个分组的平均收益
def GROUP_RATE(DATA_PATH):
    GROUP_data=pd.read_pickle(DATA_PATH)
    mean_data=GROUP_data.mean(axis=0)
    rects=plt.bar(mean_data.index.values,mean_data.values,color=['r'])
    for rect,x_lable in zip(rects,mean_data.index.values):
        height = rect.get_height()
        if height<0:
            rect.set_color('g')
        if x_lable=='buy_sell':
            rect.set_color('y')
        plt.text(rect.get_x(),1.03*height,'%f'%float(height))
    plt.xlabel('Group')
    plt.ylabel('Average Rate')
    plt.title('Group Average Rate')
    plt.show()

GROUP_PATH='Inter_Data/group_rate.pickle'
GROUP_RATE(GROUP_PATH)

#5.画出多空投资组合的净值曲线
def NETVALUE_PLOT(DATA_PATH):
    netvalue_data=pd.read_pickle(DATA_PATH)
    dates = netvalue_data.index.values
    plt.plot(netvalue_data,color='r')
    plt.xlim(dates[0], dates[-1])
    plt.xlabel('Datetime')
    plt.ylabel('NAC')
    plt.title('LongShort NAC Curve')
    plt.grid(True)
    plt.show()
    print(netvalue_data.head())

GROUP_NETVALUE_PATH='Inter_Data/BULL_SELL_NETVALUE.pickle'
NETVALUE_PLOT(GROUP_NETVALUE_PATH)



