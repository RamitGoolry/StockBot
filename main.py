def preprocess(df):
    df2 = df.setindex('timestamp')
    df2 = df2.drop('ignore', axis = 1)
    return df2