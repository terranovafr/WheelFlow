import pandas as pd
import numpy as np
from sklearn.linear_model import RidgeCV
from sklearn.feature_selection import SelectFromModel
from time import time
from sklearn.model_selection import StratifiedKFold
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import EditedNearestNeighbours
from imblearn.pipeline import Pipeline


def rename_features(df):
    # rename features 
    newNames = []
    for element in ["ACC_WV1", "ACC_WV2",  "GYR_WV1", "GYR_WV2", "MAG_WV1", "MAG_WV2","ACC", "GYR", "MAG"]:
         for feature in ["MIN", "MAX", "RANGE", "KURTOSIS", "SKEWNESS", "STD", "MEAN", "MEDIAN", "ENERGY", "Q1", "Q3", "PEAKSLEN", "RMS"]:
                newNames.append(element + "_" + feature)
    newNames.append("CLASS")
    df.columns = newNames
    return df

def z_score_standardization(series):
    return (series - series.mean()) / series.std()

def feature_selection_and_rebalancing(df, importance_index):
    X = df.iloc[:,1:-1]
    y = df.iloc[:,-1]
    
    # data normalization
    for col in X.columns:
        X[col] = z_score_standardization(X[col])

    # drop null columns
    X = X.dropna(axis='columns')

    # Feature importance
    ridge = RidgeCV(alphas=np.logspace(-6, 6, num=5)).fit(X, y)
    importance = np.abs(ridge.coef_)
    feature_names = np.array(X.columns)

    # feature selection over importance
    threshold = np.sort(importance)[importance_index] + 0.01
    tic = time()
    sfm = SelectFromModel(ridge, threshold=threshold).fit(X, y)
    toc = time()
    
    # rebalancing
    over = SMOTE(sampling_strategy='all')
    under = EditedNearestNeighbours(sampling_strategy='all')
    steps = [('o', over), ('u', under)]
    pipeline = Pipeline(steps=steps)
    X, y = pipeline.fit_resample(X, y)

    return X[feature_names[sfm.get_support()]].join(y)

def train_test(train,test,model):
    # data preparation
    x_train = train.iloc[:, :-1]
    y_train = train.iloc[:,-1]
    x_test = test.iloc[:, :-1]
    y_test = test.iloc[:,-1]

    # model fit on training set
    model.fit(x_train, y_train)

    # model test and performance calculation
    y_pred = model.predict(x_test)

    f1score = f1_score(y_test,y_pred, average='weighted')
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test,y_pred, average='weighted')
    recall = recall_score(y_test,y_pred, average='weighted')

    return accuracy, precision, recall, f1score

# K for the K-Fold cross validation
NUM_FOLDS = 10

def classify(df, clf):

    # split data and labels
    X = df.iloc[:,0:-1]
    y = df.iloc[:,-1]

    # K-Fold cross validation
    skf = StratifiedKFold(n_splits=NUM_FOLDS)
    fold_no = 1

    # sums for the results
    accuracy_sum = 0
    precision_sum = 0
    recall_sum = 0
    f1score_sum = 0

    for train_index,test_index in skf.split(X, y):
        # training set and test set split
        train = df.iloc[train_index,:]
        test = df.iloc[test_index,:]

        # classification and results update
        accuracy, precision, recall, f1score = train_test(train, test, clf)
        accuracy_sum += accuracy
        precision_sum += precision
        recall_sum += recall
        f1score_sum += f1score
        fold_no += 1

    return accuracy_sum/NUM_FOLDS, precision_sum/NUM_FOLDS, recall_sum/NUM_FOLDS, f1score_sum/NUM_FOLDS

def assign_labels(df, label):
    df.iloc[:,-1].replace(['GAIT', 'RAMP', 'STEP', 'UNEVEN'], label, inplace=True)
    return df

# constants declaration
CLASS_TYPE = ['multiclass', 'binary']

LABELS = [[0,1,2,3],[0,0,1,1]]

NAMES = [
    "Gradient Boosting",
    "Nearest Neighbors",
    "Decision Tree",
    "Random Forest",
    "Neural Net",
    "AdaBoost",
    "Naive Bayes",
]

CLASSIFIERS = [
    GradientBoostingClassifier(),
    KNeighborsClassifier(3),
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    MLPClassifier(alpha=1, max_iter=1000),
    AdaBoostClassifier(),
    GaussianNB(),
]

DATASETS = [
    pd.read_csv('data/data_segmented_05_0.csv'),
    pd.read_csv('data/data_segmented_06_03.csv'),
    pd.read_csv('data/data_segmented_08_04.csv')
]

DF_NAMES = [
    'df_05_00',
    'df_06_03',
    'df_08_04'
]

IMPORTANCE_INDEXES = [-6, -13, -21]


result_list = []
for df, df_name in zip(DATASETS, DF_NAMES):
    # Rename the features and the labels
    df = rename_features(df)
    for label, class_type in zip(LABELS, CLASS_TYPE):

        # replace labels (multiclass or binary)
        renamed_df = assign_labels(df, label)

        # perform feature selection and data rebalancing
        for index in IMPORTANCE_INDEXES:
            selected_df = feature_selection_and_rebalancing(renamed_df, index)

            for clf_name, clf in zip(NAMES, CLASSIFIERS):
                # perform classification on each classifier 
                accuracy, precision, recall, f1score = classify(selected_df, clf)
                print(f"Performed {class_type} classification with {clf_name} on the dataset {df_name} with an importance index of {str(index)}")
                row = [df_name, class_type, str(index), clf_name, accuracy, precision, recall, f1score]
                result_list.append(row)

# export clssification results
results = pd.DataFrame(result_list)
results.columns = ['df_name', 'class_type', 'num_features', 'classifier', 'avg_accuracy', 'avg_precision', 'avg_recall', 'avg_f1score']
results.to_csv('classification_results.csv', index = False)
