# linkedin_no_skills is another linkedin dataset which provides 
# the dates of job posting with job titles but not skills so it
# will not be used for skills analysis

# Cleans the data only which will be used for further analysis

# Uses: linkedin_no_skills.csv
# Produces: linkedin_no_skills_cleaned.csv

import pandas as pd
import json

# Load CSV file
df = pd.read_csv("linkedin_no_skills.csv")

# Function to extract 'datePosted' from the 'content' column
def extract_date(json_str):
    try:
        data = json.loads(json_str)
        return data.get("datePosted", None)
    except (json.JSONDecodeError, TypeError):
        return None

# Apply the function to extract 'datePosted'
df["datePosted"] = df["context"].apply(extract_date)

# Drop rows where 'datePosted' is NULL
df = df.dropna(subset=["datePosted"])

# Drop duplicate rows
df = df.drop_duplicates()

# Save cleaned data to a new CSV
df.to_csv("linkedin_no_skills_cleaned.csv", index=False)

print("Data cleaned and saved as 'linkedin_no_skills_cleaned.csv'")
