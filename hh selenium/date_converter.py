from datetime import datetime
import csv
from deep_translator import GoogleTranslator
import re

# Mapping of Russian month names to English month numbers
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

def contains_russian_letters(text):
    """Check if a string contains Russian letters."""
    return bool(re.search('[а-яА-Я]', text))

def translate_text(text):
    """Translate text if it contains Russian letters."""
    if text and contains_russian_letters(text):
        print(f"Translating: '{text}'")
        translated_text = GoogleTranslator(source='auto', target='en').translate(text)
        print(f"Translated to: '{translated_text}'")
        return translated_text
    return text

def convert_date_format(date_str):
    if not date_str:  # If date is missing, return an empty string
        return ""
    try:
        # Replace Russian month name with English equivalent
        for ru_month, en_month in russian_to_english_month.items():
            date_str = date_str.replace(ru_month, en_month)

        # Parse the converted date and format to MM/DD/YYYY
        date_obj = datetime.strptime(date_str, "%d %B %Y")
        return date_obj.strftime("%m/%d/%Y")
    except ValueError:
        return date_str  # Return original date if parsing fails

def update_dates():
    """Convert dates and translate company names in scraped_jobs.csv to save in formatted_jobs.csv."""
    updated_jobs = []
    input_file = 'scraped_jobs.csv'
    output_file = 'formatted_jobs.csv'

    # Read the input CSV and convert dates
    with open(input_file, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert the time_posted date to MM/DD/YYYY format, if available
            date_converted = convert_date_format(row['time_posted'])
            row['time_posted'] = date_converted

            # Translate the company name if it contains Russian letters
            row['company'] = translate_text(row['company'])

            # Update row and add to list
            updated_jobs.append(row)

    # Write updated data to the output CSV
    with open(output_file, mode='w', encoding='utf-8', newline='') as csvfile:
        fieldnames = updated_jobs[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_jobs)

    print(f"Dates and company names in {input_file} have been converted and saved to {output_file}.")

if __name__ == "__main__":
    update_dates()
