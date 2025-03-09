# Cleans the data and provides the Top 10 Skills for each dataset

# Uses: indeed_webscrape.csv and linkedin_historical.csv
# Produces: cleaned_indeed_data and cleaned_linkedin_data.csv

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt

# Step 1: Load the CSV files into pandas DataFrames
indeed_data = pd.read_csv('indeed_webscrape.csv')
linkedin_data = pd.read_csv("linkedin_historical.csv")

# Step 2: Clean and preprocess Indeed data
# Remove any rows where 'skills' column is NaN
# Replace NaNs with empty strings for skills
indeed_data['skills'] = indeed_data['skills'].fillna('')  

# Group Indeed data by 'job_title-href' and aggregate other columns
indeed_data_cleaned = indeed_data.groupby(['job_title-href'], as_index=False).agg({
    'job_title': 'first',
    'location': 'first',
    'company': 'first',
    # Combine unique skills
    'skills': lambda x: ', '.join(x.dropna().unique())  
})

# Step 3: Clean and preprocess LinkedIn data
linkedin_data = linkedin_data.drop_duplicates()  # Remove duplicate rows
linkedin_data['job_summary'] = linkedin_data['job_summary'].fillna("No summary available")  # Fill missing job summaries
linkedin_data = linkedin_data.dropna(subset=['job_title', 'company', 'job_skills'])  # Drop rows with missing critical columns

# Analysis Process

# Initialize TF-IDF Vectorizer
# TF-IDF is a technique used in NLP to convert textual data 
# into numerical form for machine learning models


# The TfidfVectorizer is initialized with stop_words='english' 
# and max_features=10 to focus on the most important words
# It transforms the skills data into a numerical representation where 
# more important or unique skills get higher weights.
tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=10)

# Step 4: Apply TF-IDF on Indeed data
indeed_tfidf_matrix = tfidf_vectorizer.fit_transform(indeed_data_cleaned['skills'])

# Step 5: Apply TF-IDF on LinkedIn data
linkedin_tfidf_matrix = tfidf_vectorizer.fit_transform(linkedin_data['job_skills'])

# Step 6: Get the top terms (skills)
# calculates the sum of TF-IDF scores for each skill across all job postings
# and extracts the top 10 skills with the highest scores.
top_skills_indeed_idx = indeed_tfidf_matrix.sum(axis=0).A1.argsort()[-10:][::-1]  # Get indices of top 10 skills
top_skills_linkedin_idx = linkedin_tfidf_matrix.sum(axis=0).A1.argsort()[-10:][::-1]  # Get indices of top 10 skills

top_skills_indeed = [tfidf_vectorizer.get_feature_names_out()[i] for i in top_skills_indeed_idx]
top_skills_linkedin = [tfidf_vectorizer.get_feature_names_out()[i] for i in top_skills_linkedin_idx]

top_skills_indeed_values = indeed_tfidf_matrix.sum(axis=0).A1[top_skills_indeed_idx]
top_skills_linkedin_values = linkedin_tfidf_matrix.sum(axis=0).A1[top_skills_linkedin_idx]

# Step 7: Plot the results

# Plot for Indeed data
plt.figure(figsize=(10, 6))
plt.barh(top_skills_indeed, top_skills_indeed_values, color='skyblue')
plt.title('Top Skills in Indeed Job Postings')
plt.xlabel('Sum of TF-IDF')
plt.ylabel('Skills')
plt.gca().invert_yaxis()  # To have the highest value at the top
plt.show()

# Plot for LinkedIn data
plt.figure(figsize=(10, 6))
plt.barh(top_skills_linkedin, top_skills_linkedin_values, color='lightgreen')
plt.title('Top Skills in LinkedIn Job Postings')
plt.xlabel('Sum of TF-IDF')
plt.ylabel('Skills')
plt.gca().invert_yaxis()  # To have the highest value at the top
plt.show()


# Save cleaned data to CSV files
indeed_data.to_csv("indeed_webscrape_cleaned.csv", index=False)
linkedin_data.to_csv("linkedin_historical_cleaned.csv", index=False)
