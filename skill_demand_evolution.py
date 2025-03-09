# This code provides the skill demand evolution of increasing skills.

# Uses: indeed_webscrape_cleaned.csv and linkedin_historical_cleaned.csv
# Produces: skill_demand_trends.csv and top_rising_skills.csv

import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Load cleaned datasets
indeed_data = pd.read_csv("indeed_webscrape_cleaned.csv")
linkedin_data = pd.read_csv("linkedin_historical_cleaned.csv")

# Step 2: Aggregate skill frequencies in each dataset
def extract_skills(skill_column):
    """Splits comma-separated skill strings into a list of individual skills."""
    all_skills = []
    for skills in skill_column.dropna():
        all_skills.extend(skills.lower().split(', '))
    return pd.Series(all_skills).value_counts()

# Compute skill frequencies
indeed_skill_counts = extract_skills(indeed_data['skills'])
linkedin_skill_counts = extract_skills(linkedin_data['job_skills'])

# Step 3: Merge skill frequencies into a single DataFrame
skill_trends = pd.DataFrame({
    'LinkedIn (Historical)': linkedin_skill_counts,
    'Indeed (Recent)': indeed_skill_counts
}).fillna(0)  # Fill missing values with 0 (skills that didn't appear in one dataset)

# Step 4: Calculate percentage change in skill demand
# this is based on the recent Indeed dataset and the LinkedIn dataset
skill_trends['% Change'] = ((skill_trends['Indeed (Recent)'] - skill_trends['LinkedIn (Historical)']) /
                            skill_trends['LinkedIn (Historical)'].replace(0, 1)) * 100  # Avoid division by zero

# Step 5: Identify rising skills based on the change percentage
rising_skills = skill_trends.sort_values('% Change', ascending=False).head(10)

# Remove '(required)' from skill labels
rising_skills.index = rising_skills.index.str.replace(r'\s*\(required\)', '', regex=True).str.strip()

# Step 6: Plot skill trends (only rising skills)

plt.figure(figsize=(14, 8))  # Increased height for better spacing
plt.yticks(fontsize=8)  # Reduce font size of y-axis labels
plt.barh(rising_skills.index, rising_skills['% Change'], color='green')
plt.xlabel('% Change in Demand')
plt.title('Top 10 Emerging Skills')
plt.gca().invert_yaxis()
plt.show()

# Save results
skill_trends.to_csv("skill_demand_trends.csv")
rising_skills.to_csv("top_rising_skills.csv")

print("Skill demand evolution analysis completed! Results saved as CSV files.")
