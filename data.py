import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import logging
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import comtradeapicall


logging.basicConfig(filename='comtrade_errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# API key
subscription_key = '4680c7b0d92a431e8d283f7f725a3b9d'

def fetch_data_with_backoff(reporter_code, max_retries=5):
    delay = 1
    for attempt in range(max_retries):
        try:

            mydf = comtradeapicall.getFinalData(
                subscription_key=subscription_key,
                typeCode='C',
                freqCode='A',
                clCode='HS',
                period='2023',
                reporterCode=reporter_code,
                cmdCode='ALL',
                flowCode='M',
                partnerCode=None,
                partner2Code=None,
                customsCode=None,
                motCode=None,
                format_output='JSON',
                includeDesc=True
            )
            if not mydf.empty:

                mydf = mydf[['refYear', 'reporterDesc', 'partnerDesc',
                             'primaryValue', 'flowCode','cmdDesc']].copy()
                mydf.rename(columns={
                    'refYear': 'Year',
                    'reporterDesc': 'Reporter Country',
                    'partnerDesc': 'Partner Country',
                    'primaryValue': 'Trade Value',
                    'flowCode': 'Flow Code',
                    'cmdDesc': 'Commodity',

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
                delay *= 2
            else:
                print(f"Error fetching data for reporter {reporter_code}: {e}")
                logging.error(f"Error fetching data for reporter {reporter_code}: {e}")
                return pd.DataFrame()
    print(f"Max retries exceeded for reporter {reporter_code}.")
    logging.error(f"Max retries exceeded for reporter {reporter_code}.")
    return pd.DataFrame()

def fetch_all_reporters(reporter_codes):
    all_data = pd.DataFrame()
    with ThreadPoolExecutor(max_workers=3) as executor:
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

def read_reporter_codes(file_path):
    try:
        df = pd.read_csv(file_path)
        return df['country_code'].tolist()
    except Exception as e:
        print(f"Error reading reporter codes from file: {e}")
        logging.error(f"Error reading reporter codes from file: {e}")
        return []

if __name__ == "__main__":

    input_csv = '3 - Sheet1.csv'

    reporter_codes = read_reporter_codes(input_csv)

    if reporter_codes:
        final_data = fetch_all_reporters(reporter_codes)
        if not final_data.empty:
            final_data.to_csv('comtrade_data_import.csv', index=False)
            print("Data fetching completed. Saved to 'comtrade_data.csv'.")
        else:
            print("No data fetched.")
    else:
        print("No reporter codes found. Exiting.")
        
