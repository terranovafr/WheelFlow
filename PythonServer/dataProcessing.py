import pickle
import numpy
import numpy as np
import pandas as pd
import pywt
import scipy.signal
import math

# Function to calculate the magnitude of accelerometer, gyroscope and magnitude data
def magnitude(df):
    print("Calculating magnitude...")
    dfnew = pd.DataFrame(columns=['timestamp','latitude', 'longitude', 'ACC', 'GYR', 'MAG'])
    for index, row in df.iterrows():
        dacc = math.sqrt(sum(row[i] ** 2 for i in [3,4,5]))
        dgyr = math.sqrt(sum(row[i] ** 2 for i in [6,7,8]))
        dmag = math.sqrt(sum(row[i] ** 2 for i in [9,10,11]))
        dfnew = dfnew.append({'timestamp': row[0], 'latitude': row[1], 'longitude': row[2], 'ACC': dacc, 'GYR': dgyr, 'MAG': dmag},ignore_index="True")
    return dfnew

# Function that extracts features from a signal
def extract(signal):
    min = signal.min()
    max = signal.max()
    peaks = scipy.signal.find_peaks(signal)
    return [
        min,
        max,
        max - min,
        signal.kurtosis(),
        signal.skew(),
        signal.std(),
        signal.mean(),
        signal.median(),
        (signal ** 2).sum(),
        signal.quantile(0.25),
        signal.quantile(0.75),
        len(peaks),
        math.sqrt((signal ** 2).sum() / signal.size)
    ]

# Function for the windowing and the extraction of features from the dataset
def extractFeatures(dataset):
    print("Extracting features...")
    extracted_dataset = []
    # best parameters found in the data analysis
    OFFSET = 1
    OVERLAP = 0.3
    WINDOW = 0.6
    NUM_ROWS = dataset.shape[0]
    start_index = 0
    end_index = 1
    while end_index < NUM_ROWS:
        # find windows in which consecutive rows are recorded less than 1 second apart
        while end_index < NUM_ROWS - 1 and pd.Timedelta(pd.Timestamp(dataset.iloc[end_index + 1][0]) - pd.Timestamp(
                dataset.iloc[end_index][0])).seconds < OFFSET:
            end_index += 1
        macrowindow = dataset.iloc[start_index:end_index]
        NUM_ROWS_MACRO = macrowindow.shape[0]
        start_window = 0
        end_window = 1
        # find records inside those macrowindows within a window of WINDOW seconds
        while end_window < NUM_ROWS_MACRO:
            found = -1;
            while end_window < NUM_ROWS_MACRO - 1 and pd.Timedelta(
                    pd.Timestamp(dataset.iloc[end_window + 1][0]) - pd.Timestamp(
                            dataset.iloc[start_window][0])).microseconds < WINDOW * 1000 * 1000:
                # handling the overlap, find first record apart from starting record for WINDOW - OVERLAP seconds
                if (found == -1 and pd.Timedelta(pd.Timestamp(dataset.iloc[end_window + 1][0]) - pd.Timestamp(
                        dataset.iloc[start_window][0])).microseconds >= (WINDOW - OVERLAP) * 1000 * 1000):
                    start_window = end_window + 1
                    found = 0
                end_window += 1
            window = macrowindow.iloc[start_window:end_window]
            # update indexes for segmentation
            if (found == -1):
                start_window = end_window + 1
            end_window += 1
            if window.shape[0] == 0:
                continue
            if pd.Timedelta(pd.Timestamp(window.iloc[-1][0]) - pd.Timestamp(
                    window.iloc[0][0])).microseconds < WINDOW * 1000 * 1000 / 2:
                continue
            timestamp = window.iloc[0, 0]
            latitude = window.iloc[0, 1]
            longitude = window.iloc[0,2]
            accelerometer = window.iloc[:, 3]
            gyroscope = window.iloc[:, 4]
            magnetometer = window.iloc[:, 5]
            # wavelet transformations of the signals coming from  sensors
            coefficients = []
            coeff_acc = pywt.dwt(accelerometer, wavelet='db1')
            for c in coeff_acc:
                coefficients.append(pd.Series(c))
            coeff_gyr = pywt.dwt(gyroscope, wavelet='db1')
            for c in coeff_gyr:
                coefficients.append(pd.Series(c))
            coeff_mag = pywt.dwt(magnetometer, wavelet='db1')
            for c in coeff_mag:
                coefficients.append(pd.Series(c))
            coefficients.append(accelerometer)
            coefficients.append(gyroscope)
            coefficients.append(magnetometer)
            rows = [timestamp, latitude, longitude]
            for coefficient in coefficients:
                rows = rows + extract(coefficient)
            extracted_dataset.append(rows)
        start_index = end_index + 1
        end_index += 1
    new_dataset = pd.DataFrame(extracted_dataset)
    newNames = ["timestamp", "latitude", "longitude"]
    for element in ["ACC_WV1", "ACC_WV2", "GYR_WV1", "GYR_WV2", "MAG_WV1", "MAG_WV2", "ACC", "GYR", "MAG"]:
        for feature in ["MIN", "MAX", "RANGE", "KURTOSIS", "SKEWNESS", "STD", "MEAN", "MEDIAN", "ENERGY", "Q1", "Q3",
                        "PEAKSLEN", "RMS"]:
            newNames.append(element + "_" + feature)
    new_dataset.columns = newNames
    return new_dataset

# Function for the classification of the data
def classify(df):
    print("Classifying data...")
    dataset = df.iloc[:,3:]
    loaded_model = pickle.load(open("model.pkl", 'rb'))
    classes = []
    for index, row in dataset.iterrows():
        result = loaded_model.predict(np.require([row], requirements="C"))
        if result >= 2:
            classes.append("INACCESSIBLE")
        else:
            classes.append("ACCESSIBLE")
    print("Inaccessible entries:", classes.count("INACCESSIBLE"))
    print("Accessible entries:", classes.count("ACCESSIBLE"))
    df['CLASS'] = classes
    return df

# Function for the z-score standardization
def z_score_standardization(series):
    if series.std() != 0:
        return (series - series.mean()) / series.std()
    else:
        return (series - series.mean()) + 2*numpy.random.randint(0,1,size=(len(series)))

# Function for the standardization of the entire dataset
def standardize(df):
    print("Standardizing features...")
    for col in df.columns:
        if(col != "timestamp" and col != "latitude" and col != "longitude"):
            df[col] = z_score_standardization(df[col])
    return df

# Function for the feature selection, based on the results of the data analysis
def selectFeatures(df):
    print("Selecting features...")
    return df.iloc[:,[0, 1, 2, 7, 8, 13, 19, 24, 30, 31, 36, 55, 59, 60, 77, 78, 83, 89, 90, 95, 102, 106, 107]]

# Function for the preprocessing of the data
def preprocess(df):
    print("Preprocessing dataframe...")
    df_mag = magnitude(df)
    df_ext = extractFeatures(df_mag)
    df_std = standardize(df_ext)
    df_slt = selectFeatures(df_std)
    return df_slt