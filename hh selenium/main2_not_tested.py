import pandas as pd
from deep_translator import GoogleTranslator
import re
from datetime import datetime
import csv

# Mapping of Russian month names to English month names
russian_to_english_month = {
    "января": "January",
    "февраля": "February",
    "марта": "March",
    "апреля": "April",
    "мая": "May",
    "июня": "June",
    "июля": "July",
    "августа": "August",
    "сентября": "September",
    "октября": "October",
    "ноября": "November",
    "декабря": "December"
}

def convert_date_format(date_str):
    """Convert a date string from Russian month format to MM/DD/YYYY format."""
    if not date_str:
        return ""
    try:
        for ru_month, en_month in russian_to_english_month.items():
            date_str = date_str.replace(ru_month, en_month)
        date_obj = datetime.strptime(date_str, "%d %B %Y")
        return date_obj.strftime("%m/%d/%Y")
    except ValueError:
        return date_str

def contains_russian_letters(text):
    """Check if a string contains Russian letters."""
    return bool(re.search('[а-яА-Я]', text))

def translate_text(text):
    """Translate text from Russian to English if it contains Russian letters."""
    if text and contains_russian_letters(text):
        print(f"Translating: '{text}'")
        translated_text = GoogleTranslator(source='auto', target='en').translate(text)
        print(f"Translated to: '{translated_text}'")
        return translated_text
    return text

def process_jobs_file():
    """Process the scraped_jobs.csv file: date conversion, translation, and data cleaning."""
    # Load CSV file
    df = pd.read_csv('scraped_jobs.csv')

    # Step 1: Convert 'time_posted' date format
    df['time_posted'] = df['time_posted'].apply(convert_date_format)

    # Step 2: Drop duplicates based on all columns except 'link' and 'keyword'
    df_dedup = df.drop_duplicates(subset=['title', 'company', 'location', 'salary', 'required_experience', 'skills', 'time_posted'])

    # Step 3: Ensure 'skills' column contains only strings, then expand it
    df_dedup.loc[:, 'skills'] = df_dedup['skills'].astype(str)
    df_expanded = df_dedup.assign(skills=df_dedup['skills'].str.split(', '))
    df_expanded = df_expanded.explode('skills')

    # Step 4: Remove rows with empty skills
    df_expanded = df_expanded[df_expanded['skills'].str.strip() != '']

    # Step 5: Select required columns and add the 'country' column
    df_final = df_expanded[['time_posted', 'keyword', 'skills', 'company']].copy()
    df_final['country'] = 'Uzbekistan'

    # Step 6: Translate Russian text in 'skills' and 'company' columns
    df_final['skills'] = df_final['skills'].apply(translate_text)
    df_final['company'] = df_final['company'].apply(translate_text)

    # Step 7: Save the final data to a new CSV file
    df_final.to_csv('translated_expanded_skills_in.csv', index=False)
    print("Processed data saved to 'translated_expanded_skills_in.csv'.")

if __name__ == "__main__":
    process_jobs_file()
