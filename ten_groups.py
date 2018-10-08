import pandas as pd
import numpy as np
import pickle
import time
from datetime import datetime

#1.获取合并好的数据，然后在每个时间截面按照因子大小对股票进行排序
##############################################################################################################
#更新部分：对函数参数进行修改，新增参数dd，用来判断因子IC均值的正负，来决定多空组合的方向，即是第一组减第十组，还是第十组减第一组
##############################################################################################################
def group_split(MERGE_PATH,dd):
    cols=['g0','g1','g2','g3','g4','g5','g6','g7','g8','g9']
    test_data=pd.read_pickle(MERGE_PATH)
    Dict={}
    for d,group in test_data.groupby(['DATETIME']):
        #按照因子值进行分组
        data=group.copy()
        data['factor_bin']=pd.qcut(data.factor,10)
        df = data[['factor_bin','Rate']].groupby(['factor_bin'],as_index=False).mean().sort_values(by='factor_bin',
                                                                                         ascending=True)
        print(df)
        Prate=df.Rate.values
        Dict[d]=Prate

        #按照因子值进行排序之后，然后按照因子大小进行分组
        # data=group.sort_values(by=['factor'])
        # rateLst=data.Rate.values
        # stock_num=len(rateLst)
        # N=int(stock_num/10)
        # Prate=[]
        # for i in range(9):
        #     Prate.append(np.mean(rateLst[i*N:(i+1)*N]))
        # Prate.append(np.mean(rateLst[9*N:]))
        # Dict[d]=Prate
    DATA=pd.DataFrame.from_dict(Dict,orient='index')
    DATA.columns=cols
    print(DATA)
    if dd:
        DATA=DATA.assign(buy_sell=DATA.g9-DATA.g0)
    else:
        DATA=DATA.assign(buy_sell=DATA.g0-DATA.g9)
    output=open('Inter_Data/group_rate.pickle','wb')
    pickle.dump(DATA,output)
    return DATA.mean()

#2.获取分组后的收益数据，计算多空组合的净值收益
def net_value(GROUP_PATH,DAYS):
    data=pd.read_pickle(GROUP_PATH)
    data=data.assign(netValue_ratio=data.buy_sell/100/DAYS+1)
    data=data.assign(netValue=data.netValue_ratio.cumprod())
    DATA=data.loc[:,'netValue']
    output=open('Inter_Data/BULL_SELL_NETVALUE.pickle','wb')
    pickle.dump(DATA,output)
    return DATA

#3.获取多空组合的净值数据，计算多空组合的年化收益率  #num 自然日和交易日的确定
def year_rate(testdata):
    testdata=testdata.reset_index()
    testdata.columns=['DATETIME','netvalue']
    testdata.DATETIME=testdata.DATETIME.apply(lambda s:str(s)[:10])
    dates=testdata.DATETIME.values
    start = datetime.strptime(dates[0],'%Y-%m-%d')
    end = datetime.strptime(dates[-1], '%Y-%m-%d')
    num=(end-start).days+1
    data = testdata.netvalue.values[-1]
    netValue=data**(365/num)-1
    return netValue*100

#4.获取多空组合的收益数据，计算夏普比率
def SharpRatio(yearrate,testdata):
    rate_std=np.std(testdata.values,ddof=1)*(np.sqrt(252))
    print('年化波动率为 %s'%rate_std)
    sharp_ratio=yearrate/(rate_std)
    return sharp_ratio

#5.获取多空组合的净值数据，计算多空组合的最大回撤
def MAXDOWN_Ratio(data):
    values=data.values
    maxLst=[]
    MAX=0
    for i,v in enumerate(values):
        if i==0:
            MAX=v
        else:
            if v>MAX:
                MAX=v
            else:
                maxLst.append((1-v/MAX)*100)
    MAXDOWN=max(maxLst)
    return MAXDOWN*(-1)

MERGE_PATH='Inter_Data/merged_data.pickle'
GROUP_PATH='Inter_Data/group_rate.pickle'
IC_PATH='Inter_Data/Rate5_IC.pickle'
IC_data=pd.read_pickle(IC_PATH)
IC_MEAN=np.mean(IC_data.values)
if IC_MEAN>=0:
    MEAN=group_split(MERGE_PATH,True)
else:
    MEAN=group_split(MERGE_PATH,False)
data1=pd.read_pickle('Inter_Data/group_rate.pickle')
data1.to_csv('CSV_DATA/data1_组合收益情况.csv')
data2=net_value(GROUP_PATH,5)
data2.to_csv('CSV_DATA/data2_多空组合净值.csv')
yearRate=year_rate(data2)
SR=SharpRatio(yearRate,data1.buy_sell)
MD=MAXDOWN_Ratio(data2)
Calmar=yearRate/MD

print('年化收益率为 %s'%yearRate)
print('年化夏普比率为 %s'%SR)
print('最大回撤为 %s'%MD)
print('Calmar比率为 %s'%Calmar)