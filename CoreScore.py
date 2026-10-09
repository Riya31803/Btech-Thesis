import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import logging
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import comtradeapicall


# Configure logging
logging.basicConfig(filename='comtrade_errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Your API key
subscription_key = '307df32470174bbba74cc790bdd323c0'

# Function to fetch data with rate-limiting and exponential backoff
def fetch_data_with_backoff(reporter_code, max_retries=5):
    delay = 1  # Start with a 1-second delay
    for attempt in range(max_retries):
        try:
            # Replace this with the actual API call
            mydf = comtradeapicall.getFinalData(
                subscription_key=subscription_key,
                typeCode='C',
                freqCode='A',  # 'A' for annual data
                clCode='HS',
                period='2011',  # Annual data for the year 2011
                reporterCode=reporter_code,
                cmdCode='TOTAL',  # Example: HS Codes for specific commodities
                flowCode='X',  # Example: Trade flow (Imports/Exports)
                partnerCode=None,  # Optional partner country code
                partner2Code=None,
                customsCode=None,
                motCode=None,
                format_output='JSON',  # Output format
                includeDesc=True  # Include description
            )
            if not mydf.empty:
                # Clean and rename columns
                mydf = mydf[['refYear', 'reporterDesc', 'partnerDesc',
                             'primaryValue', 'flowCode']].copy()
                mydf.rename(columns={
                    'refYear': 'Year',
                    'reporterDesc': 'Reporter Country',
                    'partnerDesc': 'Partner Country',
                    'primaryValue': 'Trade Value',
                    'flowCode': 'Flow Code',
                
                }, inplace=True)
                return mydf
            else:
                print(f"No data returned for reporter {reporter_code}.")
                return pd.DataFrame()
        except Exception as e:
            error_msg = str(e)
            if '429' in error_msg:
                print(f"Rate limit exceeded for reporter {reporter_code}. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print(f"Error fetching data for reporter {reporter_code}: {e}")
                logging.error(f"Error fetching data for reporter {reporter_code}: {e}")
                return pd.DataFrame()
    print(f"Max retries exceeded for reporter {reporter_code}.")
    logging.error(f"Max retries exceeded for reporter {reporter_code}.")
    return pd.DataFrame()

# Main function to fetch data for multiple reporters
def fetch_all_reporters(reporter_codes):
    all_data = pd.DataFrame()
    with ThreadPoolExecutor(max_workers=3) as executor:  # Adjust max_workers to control concurrency
        futures = {executor.submit(fetch_data_with_backoff, code): code for code in reporter_codes}
        for future in futures:
            reporter_code = futures[future]
            try:
                data = future.result()
                if not data.empty:
                    all_data = pd.concat([all_data, data], ignore_index=True)
            except Exception as e:
                print(f"Failed to process reporter {reporter_code}: {e}")
                logging.error(f"Failed to process reporter {reporter_code}: {e}")
    return all_data

# Function to read reporter codes from CSV
def read_reporter_codes(file_path):
    try:
        df = pd.read_csv(file_path)
        return df['Codes'].tolist()  # Assumes a column named 'country_codes'
    except Exception as e:
        print(f"Error reading reporter codes from file: {e}")
        logging.error(f"Error reading reporter codes from file: {e}")
        return []

# Fetch data and save to a CSV file
if __name__ == "__main__":
    # File path for the country codes CSV file
    input_csv = r"C:\Users\Riya\Downloads\Country codes - Sheet1 (1).csv"


    # Read reporter codes from the CSV
    reporter_codes = read_reporter_codes(input_csv)

    if reporter_codes:
        final_data = fetch_all_reporters(reporter_codes)
        if not final_data.empty:
            final_data.to_csv('comtrade_data.csv', index=False)
            print("Data fetching completed. Saved to 'comtrade_data.csv'.")
        else:
            print("No data fetched.")
    else:
        print("No reporter codes found. Exiting.")
