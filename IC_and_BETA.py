import pandas as pd
import pickle
import numpy as np
import statsmodels.api as sm

#1.获取股票数值，计算股票收益率，1日，5日，10日和20日
def stock_process(STOCKPATH,DAYS):
    stockData = pd.read_csv(STOCKPATH,encoding='gbk')
    stockData.DATETIME=pd.to_datetime(stockData.DATETIME)
    stockData=stockData[~np.isnan(stockData.VWAP)]
    data = pd.DataFrame()
    for d,group in stockData.groupby('code'):
        group=group.assign(Rate=group.CLOSE2.shift(-(DAYS+1))*100/group.CLOSE2.shift(-1)-100)
        data = data.append(group)
    rateData = data.loc[:,['DATETIME','code','INDUSTRY_SW','Rate']]
    out = open('Inter_Data/rateData.pickle','wb')
    pickle.dump(rateData,out)
    return rateData

#2.将因子数据和股票收益数据对齐，间隔天数作为外来参数传入,删除收益数值为NA的行
def data_merge(factor,rate,DAYS):
    _DICT={1:'Rate1',5:'Rate5',10:'Rate10',20:'Rate20'}
    data=pd.DataFrame()
    test= pd.merge(rate,factor,on=['DATETIME','code'])
    rateCol=_DICT[DAYS]
    for c,group in test.groupby(['code']):
        group=group.rename(columns={'FACTOR':'factor'}) \
                  .dropna(axis=0) \
                  .loc[:,['DATETIME','code','factor','Rate','INDUSTRY_SW']]
        data=data.append(group)
    output=open('Inter_Data/merged_data.pickle','wb')
    pickle.dump(data,output)
    return data,rateCol

#3.计算秩相关系数和Beta指标：均值，标准差和对应的t统计量

#3.1计算秩相关系数函数
def rankCor_get(data):
    if len(data)>1:
        data =data.loc[:,['factor','Rate']]
        # corr_mat=data.corr(method='spearman').values[1,0]
        # data=data.assign(rf=data.factor.rank(method='dense'))\
        #      .assign(rr=data.Rate.rank(method='dense'))
        # data=data.loc[:,['rf','rr']]
        # corr_mat=data.corr(method='spearman').values[1,0]
        corr_mat=data.factor.corr(data.Rate,method='spearman')
        return corr_mat
    else:
        return 'Empty'

#3.2计算因子收益函数和对应T统计量
def Beta_Tvalue_get(data):
    if len(data):
        y = data.Rate
        x = data.factor
        X = sm.add_constant(x)
        model = sm.OLS(y, X)
        fit = model.fit()
        beta = fit.params[1]
        Tvalue = fit.tvalues[1]
        return beta,Tvalue
    else:
        return 'Empty'

#3.3对齐数据调用IC计算函数并以时间为索引进行合并，计算IR和IC均值

#3.3.1计算IC，进行合并
def IC_cluster(test,col):
    DICT={}
    for d,group in test.groupby(['DATETIME']):
        res=rankCor_get(group)
        if res!='Empty':
            DICT[d]=res
    data=pd.DataFrame.from_dict(DICT,orient='index',columns=['RankIC'])
    out=open('Inter_Data/%s_IC.pickle'%col,'wb')
    pickle.dump(data,out)
    return data

#3.3.2计算IR和IC均值
def ic_indicator(data):
    IC_values=data.RankIC.values
    mean=np.mean(IC_values)
    std=np.std(IC_values,ddof=1)
    IR=mean/std
    IC_lst=[abs(v) for v in IC_values if abs(v)>0.02]
    ratio= len(IC_lst)/len(IC_values)
    indi_dict={'mean':mean,'std':std,'IR':IR,'Ratio':ratio}
    return indi_dict

#3.4对齐后的数据调用计算因子收益函数，按时间为索引进行合并，再计算均值和标准差

#3.4.1计算因子收益并合并
def Beta_cluster(test,col):
    DICT_beta,DICT_t={},{}
    for d,group in test.groupby(['DATETIME']):
        res=Beta_Tvalue_get(group)
        if res!='Empty':
            DICT_beta[d]=res[0]
            DICT_t[d]=res[1]
    BETA = pd.DataFrame.from_dict(DICT_beta,orient='index',columns=['BETA'])
    Tvalue = pd.DataFrame.from_dict(DICT_t,orient='index',columns=['Tvalue'])
    data=pd.concat([BETA,Tvalue],axis=1)
    out=open('Inter_Data/%s_BETA.pickle'%col,'wb')
    pickle.dump(data,out)
    return data

#3.4.2计算因子收益的均值，标准差和T值大于2的比率
def beta_indicator(data):
    beta=data.BETA.values
    mean=np.mean(beta)
    std=np.std(beta,ddof=1)
    IR =mean/std
    Tvalues=data.Tvalue.tolist()
    T_lst=[t for t in Tvalues if abs(t)>=2]
    ratio=len(T_lst)*100/len(Tvalues)
    return {'mean':mean,'std':std,'IR':IR,'Ratio':ratio}

#4.获取按照行业分组的股票数据，调用函数：
def indu_IC_mean(data):
    DICT={}
    #先按照行业进行分类，再按照日期分类
    for indu,group in data[0].groupby(['INDUSTRY_SW']):
        if len(np.unique(group.code.values))>5:
            IC_data=IC_cluster(group,data[1])
            IC_mean=ic_indicator(IC_data)['mean']
            DICT[indu]=IC_mean
        else:
            DICT[indu]=0
    IC_indu_mean = pd.DataFrame.from_dict(DICT, orient='index', columns=['IC_Mean'])
    out=open('Inter_Data/indu_IC_mean.pickle','wb')
    pickle.dump(IC_indu_mean,out)
    return IC_indu_mean

FACTOR_PATH='Inter_Data/netrul_factor.pickle'
STOCKPATH='Basic_Data/stockData.csv'
data=stock_process(STOCKPATH,5)
data1=pd.read_pickle('Inter_Data/rateData.pickle')
data1.to_csv('CSV_DATA/data1_计算股票收益.csv')
factor=pd.read_pickle(FACTOR_PATH)
rate=pd.read_pickle('Inter_Data/rateData.pickle')
mergeData = data_merge(factor,rate,5)
data2=pd.read_pickle('Inter_Data/merged_data.pickle')
data2.to_csv('CSV_DATA/data2_因子数据和收益数据合并.csv')
IC=IC_cluster(mergeData[0],mergeData[1])
Beta=Beta_cluster(mergeData[0],mergeData[1])
data3=pd.read_pickle('Inter_Data/Rate5_IC.pickle')
indi=ic_indicator(data3)
print(indi)
data3.to_csv('CSV_DATA/data3_IC数据.csv')
data4=pd.read_pickle('Inter_Data/Rate5_BETA.pickle')
be_indi=beta_indicator(data4)
print(be_indi)
data4.to_csv('CSV_DATA/data4_BETA数据.csv')
data_=indu_IC_mean(mergeData)
data5=pd.read_pickle('Inter_Data/indu_IC_mean.pickle')
data5.to_csv('CSV_DATA/data5_行业的IC均值.csv')
