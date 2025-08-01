# -*- coding: utf-8 -*-
"""Risk_Bank.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1I2NLwTHKmmYWpv71K_NImlqRIZ_gSyRb
"""



import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
!pip install category_encoders
import category_encoders as ce
from sklearn.preprocessing import LabelEncoder
!pip install imblearn
import imblearn
from imblearn.over_sampling import SMOTE
!pip install xgboost
!pip install opendatasets
import opendatasets as od
od.download("https://www.kaggle.com/datasets/ranadeep/credit-risk-dataset/data")

df = pd.read_csv('/content/credit-risk-dataset/loan/loan.csv')
df.head()

df.shape

df.info()

df.isnull().sum()



df.describe()



catigorical_df = []
numerical_df = []
for col in df.columns:
  if df[col].dtype == 'object':
    catigorical_df.append(col)
  elif df[col].dtype == 'int64' or df[col].dtype == 'float64':
    numerical_df.append(col)


print("catigorical columns is :",catigorical_df)
print("numerical columns is :",numerical_df)

catigorical_df = df[catigorical_df]
numerical_df = df[numerical_df]

numerical_df.head()



for col in numerical_df.columns:
  print(col)
  print(numerical_df[col].unique())
  print(numerical_df[col].value_counts(dropna=False))
  print('################################')

numerical_df = numerical_df.drop('id', axis=1)
catigorical_df = catigorical_df.drop('zip_code', axis=1)
numerical_df = numerical_df.drop('member_id', axis=1)

for col in numerical_df.columns:
   if numerical_df[col].isna().sum() > len(numerical_df[col]) * 0.70:
          numerical_df.drop(col,axis=1,inplace=True)
   elif numerical_df[col].isna().sum() < len(numerical_df[col]) * 0.10:
          # Correctly fill NaNs by assigning the result back
          numerical_df[col] = numerical_df[col].fillna(numerical_df[col].median())

# Display the first few rows to confirm changes
numerical_df.head()

numerical_df['mths_since_last_delinq'].value_counts()

num_missing = numerical_df['mths_since_last_delinq'].isna().sum()

random_values = np.random.randint(1, 41, size=num_missing)

missing_indices = numerical_df[numerical_df['mths_since_last_delinq'].isna()].index

numerical_df.loc[missing_indices, 'mths_since_last_delinq'] = random_values

numerical_df['mths_since_last_delinq'].value_counts()

threshold = 0.98

cols_to_drop = []

for col in numerical_df.columns:
    zero_ratio = (numerical_df[col] == 0.0).mean()
    if zero_ratio >= threshold:
        cols_to_drop.append(col)

numerical_df.info()

numerical_df.head()

numerical_df['policy_code'].value_counts()

numerical_df = numerical_df.drop('policy_code', axis=1)

threshold = 0.95

low_variance_cols = []

for col in numerical_df.columns:
    top_freq = numerical_df[col].value_counts(normalize=True).iloc[0]  # proportion of most frequent value
    if top_freq >= threshold:
        low_variance_cols.append(col)

numerical_df.drop(columns=low_variance_cols, inplace=True)
print("Columns with low variance:", low_variance_cols)
print("columns with low variance are dropped :", low_variance_cols )

numerical_df.info()

numerical_df.head()

def remove_outliers(numerical_df, column):
    Q1 = numerical_df[column].quantile(0.25)
    Q3 = numerical_df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    numerical_df[column] = np.where(numerical_df[column] > upper_bound, upper_bound, numerical_df[column])
    numerical_df[column] = np.where(numerical_df[column] < lower_bound, lower_bound, numerical_df[column])

    return numerical_df

def skewed_data(numerical_df):
    for col in numerical_df.columns:
        if abs(numerical_df[col].skew()) > 1:
            numerical_df = remove_outliers(numerical_df, col)
            numerical_df[col] = np.log1p(numerical_df[col])
    return numerical_df

skewed_data(numerical_df)

numerical_df.hist(figsize=(30,20))

import matplotlib.pyplot as plt
import seaborn as sns

# Calculate the correlation matrix
correlation_matrix = numerical_df.corr()

# Plot the heatmap
plt.figure(figsize=(15, 10)) # Adjust figure size as needed
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm') # annot=True can be too cluttered for many columns
plt.title('Correlation Matrix of Numerical Features')
plt.show()

catigorical_df.info()

for col in catigorical_df.columns:
  print(col)
  print(catigorical_df[col].value_counts(dropna=False, normalize=True))
  print('################################')

catigorical_df.isna().sum()

catigorical_df = catigorical_df.drop('url', axis=1)

threshold = 0.95

cols_to_drop = []

for col in catigorical_df.columns:
    zero_ratio = (catigorical_df[col] == 0.0).mean()
    if zero_ratio >= threshold:
        cols_to_drop.append(col)
        print(col)

catigorical_df.info()

print(catigorical_df['verification_status_joint'].value_counts(dropna=False))

catigorical_df = catigorical_df.drop('verification_status_joint', axis=1)

catigorical_df.info()

threshold = 0.99

low_variance_cols = []

for col in numerical_df.columns:
    top_freq = numerical_df[col].value_counts(normalize=True).iloc[0]  # proportion of most frequent value
    if top_freq >= threshold:
        low_variance_cols.append(col)

numerical_df.drop(columns=low_variance_cols, inplace=True)
print("columns with low variance are dropped :", low_variance_cols )

catigorical_df.info()

catigorical_df['earliest_cr_line'] = pd.to_datetime(catigorical_df['earliest_cr_line'])
catigorical_df['last_pymnt_d'] = pd.to_datetime(catigorical_df['last_pymnt_d'])
catigorical_df['last_credit_pull_d'] = pd.to_datetime(catigorical_df['last_credit_pull_d'])
catigorical_df['next_pymnt_d'] = pd.to_datetime(catigorical_df['next_pymnt_d'])
catigorical_df['issue_d'] = pd.to_datetime(catigorical_df['issue_d'])
catigorical_df.info()

cat_cols = df.select_dtypes(include='object').columns
for col in cat_cols:
    df[col] = df[col].fillna(df[col].mode()[0])

catigorical_df.info()

catigorical_df['next_pymnt_d'].value_counts()

date = ['issue_d', 'earliest_cr_line', 'last_pymnt_d', 'last_credit_pull_d', 'next_pymnt_d']
date = catigorical_df[date]
date.info()

# Ensure 'next_pymnt_d' in catigorical_df is in datetime format
# Use errors='coerce' to turn unparseable dates into NaT (Not a Time)
catigorical_df['next_pymnt_d'] = pd.to_datetime(catigorical_df['next_pymnt_d'], errors='coerce')

# Extract date components if the column is in datetime format
if pd.api.types.is_datetime64_any_dtype(catigorical_df['next_pymnt_d']):
    catigorical_df['next_pymnt_month'] = catigorical_df['next_pymnt_d'].dt.month
    catigorical_df['next_pymnt_year'] = catigorical_df['next_pymnt_d'].dt.year
    catigorical_df['next_pymnt_day'] = catigorical_df['next_pymnt_d'].dt.day

    # Fill NaN values created by NaT and original NaNs
    catigorical_df['next_pymnt_month'] = catigorical_df['next_pymnt_month'].fillna(0)
    catigorical_df['next_pymnt_year'] = catigorical_df['next_pymnt_year'].fillna(0)
    catigorical_df['next_pymnt_day'] = catigorical_df['next_pymnt_day'].fillna(0)

    # Drop the original datetime column
    catigorical_df = catigorical_df.drop('next_pymnt_d', axis=1)

    print("Date components extracted and original column dropped.")
else:
    print("Could not convert 'next_pymnt_d' to datetime.")

# Display info to check the new columns and dropped column
catigorical_df.info()

import pandas as pd

# Create a DataFrame to hold new features
datetime_features = pd.DataFrame()

# Iterate through columns in catigorical_df
for col in catigorical_df.columns.tolist():  # Use .tolist() to avoid issues during iteration
    if pd.api.types.is_datetime64_any_dtype(catigorical_df[col]) or 'date' in col.lower() or col.endswith('_d'):
        print(f"⏳ Processing datetime column: {col}")

        # 1. Convert column to datetime safely
        dt_col = pd.to_datetime(catigorical_df[col], errors='coerce')

        # 2. Drop original column
        catigorical_df.drop(columns=col, inplace=True)

        # 3. Extract components
        datetime_features[f'{col}_year'] = dt_col.dt.year
        datetime_features[f'{col}_month'] = dt_col.dt.month
        datetime_features[f'{col}_day'] = dt_col.dt.day

        # 4. Fill missing with mode
        for comp in ['year', 'month', 'day']:
            feature = f'{col}_{comp}'
            mode_val = datetime_features[feature].mode()[0]
            datetime_features[feature].fillna(mode_val)

        print(f"✅ Extracted: {col}_year, {col}_month, {col}_day")
    else:
        print(f"❌ Skipped: {col} (not a datetime column)")

# Merge extracted features back
catigorical_df = pd.concat([catigorical_df, datetime_features], axis=1)

catigorical_df.info()

catigorical_df.isnull().sum()

catigorical_df['desc'].fillna('No Description')

catigorical_df = catigorical_df.fillna('No Description')

""" import pandas as pd
from sklearn.preprocessing import LabelEncoder

df_encoded = catigorical_df.copy()

for col in df_encoded.columns:
    unique_vals = df_encoded[col].nunique(dropna=True)

    if unique_vals > 4:
        # Use a new LabelEncoder per column to avoid leakage
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
        print(f"✅ Label Encoded column: {col} (unique values: {unique_vals})")
    elif unique_vals <= 4:
        # Fill NaN values with the mode before one-hot encoding
        df_encoded[col] = df_encoded[col].fillna(df_encoded[col].mode()[0])
        dummies = pd.get_dummies(df_encoded[col], prefix=col, drop_first=True, dtype=int)
        # Concatenate the new dummy columns and drop the original column
        df_encoded = pd.concat([df_encoded.drop(columns=[col]), dummies], axis=1)
        print(f"✅ One-Hot Encoded column: {col} (unique values: {unique_vals})")

# Result: df_encoded contains all encoded categorical features

"""

!pip install imblearn
!pip install xgboost
from xgboost import XGBClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import train_test_split

from sklearn.decomposition import PCA

catigorical_df.info()



import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
!pip install category_encoders
import category_encoders as ce
from sklearn.preprocessing import LabelEncoder

X = catigorical_df.drop('loan_status', axis=1)
y = catigorical_df['loan_status']
X = pd.concat([X, numerical_df], axis=1)
# Encode the target variable
leble = LabelEncoder()
y_encoded = leble.fit_transform(y)


# 🧪 Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, shuffle=True
)

# 🎯 Use TargetEncoder on categorical columns
categorical_cols = X.columns.tolist()

# ✅ Fit encoder only on training data (to avoid data leakage)
encoder = ce.TargetEncoder(cols=categorical_cols)
X_train_encoded = encoder.fit_transform(X_train, y_train)
X_test_encoded = encoder.transform(X_test)  # Only transform test data

# 🔷 Apply PCA
pca = PCA(n_components=10)
X_train_pca = pca.fit_transform(X_train_encoded)
X_test_pca = pca.transform(X_test_encoded)

# ⚖️ Apply SMOTE only if needed (e.g., class imbalance)
from imblearn.over_sampling import SMOTE
sm = SMOTE(random_state=42)
X_train_pca, y_train= sm.fit_resample(X_train_pca, y_train)

import joblib
model = XGBClassifier(use_label_encoder=True, eval_metric='logloss', random_state=42)
model.fit(X_train_pca, y_train)
y_pred = model.predict(X_test_pca)

# 🧪 Predict and evaluate
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Accuracy: {accuracy:.4f}")

joblib.dump(model, "model.pkl")

# Save column order before PCA
joblib.dump(X_train_encoded.columns.tolist(), "features.pkl")
print("Model saved. Accuracy:", accuracy_score(y_test,y_pred ))

joblib.dump(model, "model.pkl")

# Save column order before PCA
joblib.dump(X_train_encoded.columns.tolist(), "features.pkl")
print("Model saved. Accuracy:", accuracy_score(y_test,y_pred ))

import streamlit as st
import pandas as pd
import numpy as np
import joblib

# Load model and column names
model = joblib.load("model.pkl")
columns = joblib.load("features.pkl")

st.title("🏦 Credit Risk Prediction App")
st.write("Enter applicant details to predict the credit risk")

# Create input form dynamically
input_data = {}
for col in columns:
    if "int" in col or "num" in col or "amt" in col:
        input_data[col] = st.number_input(f"{col}", value=0)
    else:
        input_data[col] = st.text_input(f"{col}")

# Submit
if st.button("Predict"):
    input_df = pd.DataFrame([input_data])
    input_df = pd.get_dummies(input_df).reindex(columns=columns, fill_value=0)
    prediction = model.predict(input_df)[0]
    st.success(f"Prediction: {'Approved' if prediction == 1 else 'Rejected'}")