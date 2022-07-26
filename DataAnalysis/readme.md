# WheelFlow Data Analysis

In this repository you can find all the code used for analyzing the data collected by the RecordApplication in the first stage of the WheelFlow project.

## The [`data_analysis.py`](./data_analysis.py) file

In this file you can find the final pipeline used for the data analysis, following the segmentation tasks.  
The script written in this file:  
1. imports the segmented datasets from `.csv` files contained in the [data folder](./data)   
    
    then, for each dataset

2. renames the features and converts the class labels into numerical attributes according to the classification type (binary or multiclass)
3. performs normalization, feature selection and rebalancing using different importance indexes for the feature selection task  

    finally, for each combination of dataset, classification type and importance index on feature selection

4. performs a 10-fold cross-validation using different classifiers
5. appends the results in the [`classification_results.csv`](./classification_results.csv) file.

## Notebooks in the [python](./python) folder

In this folder there are notebooks for each single step of the data analysis, including some of the steps of the final pipeline descripted before, like the [classification notebook](./python/classification.ipynb), [addColumnsName notebook](./python/addColumnsName.ipynb), the three feature selection notebooks, one for [binary classification](./python/featureselection_binary.ipynb), one for [multiclassclassification](./python/featureselection_allClasses.ipynb), and one [more general](./python/featureselection.ipynb).

There are also some notebooks used to visualize and plot the data, like the [data visualization notebook](./python/datavisualization.ipynb) and the [PCA notebook](./python/PCA.ipynb) used to plot data in two dimensions.

### [data cleaning notebook](./python/datacleaning.ipynb)

In this notebook the raw data received from the smartphone sensors is cleaned and prepared for the data segmentation and the feature extraction.  

The `.csv` data were imported, and the script removes the rows in which 2/3 of the features are 0 (non-meaningful record); then the three columns from each smartphone sensor are aggregated with the norm of the three coordinates (i. e. `ACC_X`, `ACC_Y`, `ACC_Z` -> `ACC` = `|ACC_X^2 + ACC_Y^2 + ACC_Z^2|`)

### [segmentation notebook](./python/segmentation.ipynb)  

This notebook contains the code for segmenting the already cleaned data and extracting the final features from each window.  

First, the script creates the *macro windows*, one for each recording, and from each macro window it creates the actual windows.

Once a window is defined, the features from the time domain (one for each sensor) are transformed using the **wavelet transformation**, obtaining 2 more features for each sensor.

Finally, from each window the script extracts the aggregated final features, and exports the final dataset in a `.csv` file.

You can specify three segmentation parameters:
- `OFFSET`: the distance between two different macro windows, in seconds
- `WINDOW`: the width of a single time window, expressed in seconds
- `OVERLAP`: how much two adjacent windows will overlap each other

The features extracted from each window are min, max, difference between min and max, kurtosis, skewness, mean, standard deviation, median, energy, first and third quartile, and the number of peaks for each cleaned feature, with a total of 117 features.
