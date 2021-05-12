#print("")
#print ('\033[31;42;1m' + '' + '\033[0m')
import time
import seaborn
import cv2
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
import pickle
#Setting rows and coloums limits
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

'''
plt.xlabel('x label')
plt.ylabel('y label')
plt.title("Fig2")
plt.show(block=True)
plt.interactive(False)
cv2.waitKey(0)
cv2.destroyAllWindows()
'''

df1 = pd.read_csv('home.csv') #Reading CSV FILE
df2 = df1.drop(['area_type' , 'society' , 'balcony' , 'availability'  ] , axis='columns') #Dropping fields that have less role in predicting the price
df3 = df2.dropna() #Dropping the rows which have "na" value
df3['bhk'] = df3['size'].apply( lambda x : int(x.split(' ')[0] )) #Converting our size coloumn to number for the purpose of data evaluation
#Handling non uniform datas in total_sqft coloumns
def convert (x):
    t = x.split('-')
    if(len(t)==2):
        return (float(t[0])+float(t[1]))/2
    try :
        return (float(x))
    except:
        return None

df4 = df3.copy()
df4['total_sqft'] = df4['total_sqft'].apply(convert)
df4=df4.dropna()

#Feature Engineering

df5=df4.copy()
df5['price_per_sqft'] = df5['price']*100000/df5['total_sqft']

#Reducing Dimensionality curse for location coloumn
df5.location=df5.location.apply(lambda  x: x.strip()) #Removing trailing or extra spaces
loc_stat = df5.groupby('location')['location'].agg('count').sort_values(ascending=False)
loc_stat = loc_stat[loc_stat<=10] #We will take values where stats are less than 10 and assign 'other' in location coloumn
df5.location=df5.location.apply(lambda x: 'other' if x in loc_stat else x)

# *Outlier detection **************************************************************************************************************************

# We will remove rows that have unexpected data
df6 = df5[~(df5.total_sqft / df5.bhk < 300 )]
# Removal using Standard Deviation and Mean , we will chooose loactions one by one and drop those rows whose values don't lie in m-st to m+st range
def remove(df):
    df_out = pd.DataFrame()
    for key, subdf in df.groupby('location'):
        m = np.mean(subdf.price_per_sqft)
        st = np.std(subdf.price_per_sqft)
        reduced_df = subdf[(subdf.price_per_sqft>(m-st)) & (subdf.price_per_sqft<=(m+st))] #One standard deviations
        df_out = pd.concat([df_out,reduced_df],ignore_index=True)
    return df_out

df7 = remove(df6)
# We should also remove, where for same location, the price of (for example) 3 bedroom apartment is less than 2 bedroom apartment (with same square ft area).
def remove_bhk_outliers(df):
    exclude_indices = np.array([])
    for location, location_df in df.groupby('location'):
        bhk_stats = {}
        for bhk, bhk_df in location_df.groupby('bhk'):
            bhk_stats[bhk] = {
                'mean': np.mean(bhk_df.price_per_sqft),
                'std': np.std(bhk_df.price_per_sqft),
                'count': bhk_df.shape[0]
            }
        for bhk, bhk_df in location_df.groupby('bhk'):
            stats = bhk_stats.get(bhk-1)
            if stats and stats['count']>5:
                exclude_indices = np.append(exclude_indices, bhk_df[bhk_df.price_per_sqft<(stats['mean'])].index.values)
    return df.drop(exclude_indices,axis='index')
df8 = remove_bhk_outliers(df7)

# Removing data rows which have unusual data for bathrooms

df9 = df8[ df8.bath < df8.bhk+2]
df10 = df9.drop(['size' , 'price_per_sqft' ] , axis='columns') #Dropping fields that are not to be used
dummies = pd.get_dummies(df10.location)
df11 = pd.concat([df10,dummies.drop('other',axis='columns')],axis='columns')
df12 = df11.drop('location',axis='columns')

#Building the ML Model Now

X = df12.drop(['price'],axis='columns')
y = df12.price

# Can be used to find best model and we concluded linear Regression is best so we will use it
'''
from sklearn.model_selection import GridSearchCV

from sklearn.linear_model import Lasso
from sklearn.tree import DecisionTreeRegressor

from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import cross_val_score

cv = ShuffleSplit(n_splits=5, test_size=0.2, random_state=0)

def find_best_model_using_gridsearchcv(X,y):
    algos = {
        'linear_regression' : {
            'model': LinearRegression(),
            'params': {
                'normalize': [True, False]
            }
        },
        'lasso': {
            'model': Lasso(),
            'params': {
                'alpha': [1,2],
                'selection': ['random', 'cyclic']
            }
        },
        'decision_tree': {
            'model': DecisionTreeRegressor(),
            'params': {
                'criterion' : ['mse','friedman_mse'],
                'splitter': ['best','random']
            }
        }
    }
    scores = []
    cv = ShuffleSplit(n_splits=5, test_size=0.2, random_state=0)
    for algo_name, config in algos.items():
        gs =  GridSearchCV(config['model'], config['params'], cv=cv, return_train_score=False)
        gs.fit(X,y)
        scores.append({
            'model': algo_name,
            'best_score': gs.best_score_,
            'best_params': gs.best_params_
        })

        return pd.DataFrame(scores, columns=['model', 'best_score', 'best_params'])

find_best_model_using_gridsearchcv(X, y)
'''

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=10)

from sklearn.linear_model import LinearRegression
lr_clf = LinearRegression()
lr_clf.fit(X_train,y_train)

def predict_price(location,sqft,bath,bhk):
    loc_index = np.where(X.columns==location)[0][0]

    x = np.zeros(len(X.columns))
    x[0] = sqft
    x[1] = bath
    x[2] = bhk
    if loc_index >= 0:
        x[loc_index] = 1
    return lr_clf.predict([x])[0]
import pickle
with open('home.pickle','wb') as f:
    pickle.dump(lr_clf,f)

import json
columns = {
    'data_columns' : [col.lower() for col in X.columns]
}
with open("home.json","w") as f:
    f.write(json.dumps(columns))

