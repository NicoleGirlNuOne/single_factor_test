import pandas as pd
import numpy as np
import pickle

#1.读取因子数据进行缺失值处理：全部进行删除
def delete_na(FACTOR_PATH):
    factordata = pd.read_csv(FACTOR_PATH,header=0)
    factordata.DATETIME=pd.to_datetime(factordata.DATETIME)
    factor_tech = factordata.iloc[:,[0,1,3]]\
                  .dropna(axis = 0)
    factor_tech.columns = ['DATETIME','FACTOR','code']
    output = open('Inter_Data/No_nan_factor.pickle','wb')
    pickle.dump(factor_tech,output)
    return factor_tech.copy()

#2.读取因子数据进行极端值处理：上下界为 中位数+-3*1.4826*绝对中位数,将不在范围内的异常数据删除
def delete_extreme(factordata):
    factorCopy = factordata.copy()
    factors = factorCopy.iloc[:,1].values
    med = np.median(factors)
    factorCopy= factorCopy.assign(inter= abs(factorCopy.iloc[:,1]-med))
    INTER = factorCopy.inter.values
    MED = np.median(INTER)
    UP = med+3*1.4826*MED
    DOWN = med-3*1.4826*MED
    print(UP)
    print(DOWN)
    factordata=factordata[(factordata.FACTOR<=UP)&(factordata.FACTOR>=DOWN)]
    return factordata

#3.读取因子数据进行标准化处理：Z_score,使因子数据符合正态分布
def standard(factorsdata):
    factorsCopy = factorsdata.copy()
    factor = factorsCopy.iloc[:,1].values
    mean = np.mean(factor)
    std = np.std(factor,ddof=1)
    factorsdata.FACTOR=(factorsdata.FACTOR-mean)/std
    return factorsdata.copy()

#4.读取原始数据，以时间截面分组，处理后的数据再进行拼接
def data_link(testdata):
    DATA1=pd.DataFrame()
    DATA2=DATA1.copy()
    for d,data in testdata.groupby(['DATETIME']):
        _data=delete_extreme(data)
        DATA1=DATA1.append(_data)
        print(_data)
        _data_=standard(_data)
        print(_data_)
        DATA2=DATA2.append(_data_)
    out1=open('Inter_Data/No_extreme_factor.pickle','wb')
    pickle.dump(DATA1,out1)
    out2=open('Inter_Data/Standarded_factor.pickle','wb')
    pickle.dump(DATA2,out2)
    return DATA1,DATA2

FACTOR_PATH='Basic_Data/factorData.csv'
data_no_na=delete_na(FACTOR_PATH)
data1=pd.read_pickle('Inter_Data/No_nan_factor.pickle')
data1.to_csv('CSV_DATA/data1_删除NA值.csv')
data_s=data_link(data1)
data2=pd.read_pickle('Inter_Data/No_extreme_factor.pickle')
data2.to_csv('CSV_DATA/data2_删除极端值.csv')
data3=pd.read_pickle('Inter_Data/Standarded_factor.pickle')
data3.to_csv('CSV_DATA/data3_因子数值标准化.csv')
























