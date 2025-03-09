# This code displays the time series visualization of job
# trends. Times Series means a graph where the x-axis represents 
# time and the y-axis represents job trends

# Uses: linkedin_no_skills_cleaned.csv (we need to use the dataset with dates)
# Produces: A graph of the job postings over time 

import pandas as pd
import matplotlib.pyplot as plt

linkedin_recent = pd.read_csv("linkedin_no_skills_cleaned.csv")

# Convert date to datetime format
linkedin_recent['datePosted'] = pd.to_datetime(linkedin_recent['datePosted'])

# Aggregate by month
linkedin_recent['year_month'] = linkedin_recent['datePosted'].dt.to_period('M')
job_trends = linkedin_recent.groupby('year_month').size()

# Plot job postings over time
plt.figure(figsize=(10, 5))
job_trends.plot(kind='line', marker='o', color='blue')
plt.title("LinkedIn Job Postings Over Time")
plt.xlabel("Month (2021)")
plt.ylabel("Number of Job Postings")
plt.xticks(rotation=45)
plt.grid()
plt.show()
