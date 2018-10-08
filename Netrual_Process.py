import pandas as pd
import numpy as np
import math
import statsmodels.api as sm
import pickle

#1.读取股票数据：设置行业哑变量
def stock_process():
    stockData = pd.read_csv('Basic_Data/stockData.csv',encoding='gbk')
    print(stockData.columns)
    stockData.DATETIME=pd.to_datetime(stockData.DATETIME)
    stockData=stockData[~np.isnan(stockData.VWAP)]
    print(stockData.VWAP)
    stockData = stockData.assign(mktValueLog=(stockData.CLOSE*stockData.TOTAL_SHARES).apply(lambda s:math.log(s)))
    interData = stockData.loc[:,['DATETIME','code','INDUSTRY_SW','mktValueLog']]\
                .assign(flag =1)
    INTERDATA = interData.pivot_table(index=['DATETIME','code','mktValueLog'],columns=['INDUSTRY_SW'],values='flag',fill_value=0)\
                .reset_index()
    out = open('Inter_Data/INTERDATA.pickle','wb')
    pickle.dump(INTERDATA,out)
    return INTERDATA

#2.读取单因子数据，处理过的股票数据进行合并，然后回归对因子进行中性化。中性化过程：
def factor_netrul(FACTOR_PATH,STOCK_PATH):
    factor = pd.read_pickle(FACTOR_PATH)
    stock = pd.read_pickle(STOCK_PATH)
    testData = pd.merge(factor,stock,on =['DATETIME','code'])
    testData = testData.sort_values(by=['DATETIME','code'])
    pre_Cols= testData.loc[:,['DATETIME','code']]
    resid_factor = pd.Series()
    for d,group in testData.groupby('DATETIME'):
        print(group)
        y = group.FACTOR
        x = group.iloc[:,3:-1]
        X = sm.add_constant(x)
        model = sm.OLS(y, X)
        res = model.fit()
        netrul_factor = res.resid
        resid_factor=resid_factor.append(netrul_factor)
    testData = pd.concat([pre_Cols,resid_factor],axis=1)
    print(testData.head(100))
    testData.columns = ['DATETIME','code','FACTOR']
    out = open('Inter_Data/netrul_factor.pickle','wb')
    pickle.dump(testData,out)
    return testData

data=stock_process()
FACTOR_PATH= 'Inter_Data/Standarded_factor.pickle'
STOCK_PATH= 'Inter_Data/INTERDATA.pickle'
data1=pd.read_pickle('Inter_Data/INTERDATA.pickle')
data1.to_csv('CSV_DATA/data1_设置行业哑变量.csv')
res = factor_netrul(FACTOR_PATH,STOCK_PATH)
data2=pd.read_pickle('Inter_Data/netrul_factor.pickle')
data2.to_csv('CSV_DATA/data2_因子数值中心化.csv')



















