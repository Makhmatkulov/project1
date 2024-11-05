import pandas as pd
import re
from deep_translator import GoogleTranslator

# Load the CSV file with updated dates and translated company names
df = pd.read_csv('formatted_jobs.csv')

# Step 1: Drop duplicates based on all columns except 'link' and 'keyword'
df_dedup = df.drop_duplicates(subset=['title', 'company', 'location', 'salary', 'required_experience', 'skills', 'time_posted'])

# Step 2: Ensure 'skills' column contains only strings, then expand it
df_dedup.loc[:, 'skills'] = df_dedup['skills'].astype(str)
df_expanded = df_dedup.assign(skills=df_dedup['skills'].str.split(', '))
df_expanded = df_expanded.explode('skills')

# Step 3: Remove rows with empty skills
df_expanded = df_expanded[df_expanded['skills'].str.strip() != '']

# Step 4: Select only the required columns and add the 'country' column
df_final = df_expanded[['time_posted', 'keyword', 'skills', 'company']].copy()
df_final['country'] = 'Uzbekistan'

# Function to check if a string contains Russian letters
def contains_russian_letters(text):
    return bool(re.search('[а-яА-Я]', text))

# Function to translate text if it contains Russian letters
def translate_text(text):
    if text and contains_russian_letters(text):
        print(f"Translating: '{text}'")
        translated_text = GoogleTranslator(source='auto', target='en').translate(text)
        print(f"Translated to: '{translated_text}'")
        return translated_text
    return text

# Apply translation to the 'skills' column only
df_final['skills'] = df_final['skills'].apply(translate_text)

# Save the final data to a new CSV file
df_final.to_csv('translated_expanded_skills_in.csv', index=False)

print("Duplicates removed, skills expanded, empty skills filtered out, Russian text in skills translated, and final CSV created successfully!")
