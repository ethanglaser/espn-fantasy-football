import os
import pandas as pd
import xgboost as xg
import numpy as np
from sklearn.metrics import mean_squared_error


column_renames = {'Pick Rating (1 worst, 10 best)': 'rating', 'Position-Based Draft Pick': 'position_draft', 'Position-Based Season Finish': 'position_finish', 'Overall Draft Pick': 'ovr_draft', 'Overall Season Finish': 'ovr_finish', 'Total Points': 'pts_total', 'Number of Weeks Missed': 'wks_out', 'Average Weekly Scoring': 'pts_avg', 'Position': 'pos'}
drop_for_training = ["Player Name", "Fantasy Team", "Position", "League", "Season", "Evaluator", "pts_total", "pts_avg"]

def evaluate(test_year, drop_cols, position_normalize_cols, general_normalize_cols):
    # read in every excel file in the Training folder
    # process file, dropping specified columns and normalizing others based on that specific file
    # add file to train or test data depending on year
    # train model and evaluate
    train_data = []
    test_data = []
    for excel in os.listdir(os.curdir + '/Training'):
        current = pd.read_excel(os.curdir + '/Training/' + excel)
        current = initial_processing(current)
        current = process_season(current, drop_cols, position_normalize_cols, general_normalize_cols)
        current['League'] = excel.split('-')[0]
        current['Season'] = excel.split('-')[1]
        current['Evaluator'] = excel.split('-')[2].split('.')[0]
        if excel.split('-')[1] == test_year:
            test_data.append(current)
        else:
            train_data.append(current)
    
    train_data = pd.concat(train_data)
    test_data = pd.concat(test_data)
    train_data.fillna(dict.fromkeys([col for col in train_data.columns if col[:4] == "pos_"], 0), inplace=True)
    test_data.fillna(dict.fromkeys([col for col in test_data.columns if col[:4] == "pos_"], 0), inplace=True)
    train_data = train_data.dropna()
    test_data = test_data.dropna()
    
    train_X = train_data.drop(columns=drop_for_training + ['rating'])
    train_Y = train_data['rating']
    test_X = test_data.drop(columns=drop_for_training + ['rating'])
    test_Y = test_data['rating']

    model = xg.XGBRegressor()
    model.fit(train_X, train_Y)
    predictions = model.predict(test_X)
    test_X['rating'] = test_Y
    test_X['predicted'] = predictions
    test_X['error'] = np.abs(test_X['rating'] - test_X['predicted'])
    test_X.to_csv("temp" + str(test_year) + ".csv")
    return np.sqrt(mean_squared_error(test_Y, predictions))




def process_season(df, drop_cols, position_normalize_cols, general_normalize_cols):
    # drop specified columns
    df = df.drop(columns=drop_cols)
    # normalize specified columns
    for col in position_normalize_cols:
        #TODO pull out col after grouping by position
        groups = df.groupby('Position')[col]
        df['normal_' + col] = groups.transform(lambda x: (x - x.mean()) / x.std())
    for col in general_normalize_cols:
        df['normal_' + col] = (df[col] - df[col].mean()) / df[col].std()
    # return processed dataframe
    return df


def initial_processing(current):
    current = current.rename(columns=column_renames)
    if "Points in Final 8 Weeks" in current.columns:
        current = current.drop(columns=["Points in Final 8 Weeks"])
    current = current.dropna()
    current['Position'] = current[column_renames['Position']]
    current = pd.get_dummies(current, columns=[column_renames["Position"]], prefix=column_renames["Position"])
    current[column_renames["Position-Based Draft Pick"]] = current[column_renames["Position-Based Draft Pick"]].str.extract(r"[A-Z]+-(\d+)").astype(int)
    current[column_renames["Position-Based Season Finish"]] = current[column_renames["Position-Based Season Finish"]].str.extract(r"[A-Z]+-(\d+)").astype(int)  
    current = current.replace({column_renames["Position-Based Season Finish"]: 0}, 100)
    return current

def get_human_based_rmse():
    training_files = os.listdir(os.curdir + '/Training')
    total_ratings = 0
    total_squared_error = 0
    for index, excel in enumerate(training_files):
        ratings1 = pd.read_excel(os.curdir + '/Training/' + excel)['Pick Rating (1 worst, 10 best)']
        for excel2 in training_files[index+1:]:
            if excel.split('-')[0] == excel2.split('-')[0] and excel.split('-')[1] == excel2.split('-')[1]:
                ratings2 = pd.read_excel(os.curdir + '/Training/' + excel2)['Pick Rating (1 worst, 10 best)']
                ratings = pd.concat([ratings1.rename('1'), ratings2.rename('2')], axis=1)
                ratings = ratings.dropna()
                print(np.sqrt(mean_squared_error(ratings['1'], ratings['2'])))
                # for r1, r2 in zip(ratings1, ratings2):
                #     if r1.isnumeric() and not r2.isnumeric():
                #         total_ratings += 1
                #         total_squared_error += (r1 - r2) ** 2
                #     else:
                #         print(r1, r2)

    return np.sqrt(total_squared_error / total_ratings)
                    



if __name__ == '__main__':
    for year in ['2018', '2019', '2020', '2021']:
        print(year + " rmse: " + str(evaluate(year, [], ['pts_total', 'pts_avg'], [])))
    print("Human-based rmse: " + str(get_human_based_rmse()))