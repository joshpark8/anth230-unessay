import pandas as pd
from plotly import express as px
import os

pwd = os.getcwd()
data_path = f"{pwd}/anth230-unessay/UN Women/labor participation.csv"
df = pd.read_csv(data_path)

# Quick look at the data
print("Initial Data Preview:")
print(df.head())

# Basic Data Cleaning
# Example: normalize column names by stripping spaces and converting to lowercase
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
df.dropna(inplace=True)  # Remove missing values (adjust this as needed)

# Visualizing Wage Distribution by Gender
fig_wage = px.box(
    df,
    x="gender",   # Make sure this matches your actual column name
    y="wage",     # Make sure this matches your actual column name
    title="Wage Distribution by Gender"
)
fig_wage.show()

# # Visualizing Education Levels by Gender
# fig_edu = px.histogram(
#     df,
#     x="education_level",  # Update this column name based on your dataset
#     color="gender",
#     title="Education Levels by Gender"
# )
# fig_edu.show()