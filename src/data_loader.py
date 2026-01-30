import pandas as pd

## Data Loader Class
class AnimeDataloader:
    def __init__(self, original_csv:str , processed_csv:str):
        self.original_csv = original_csv
        self.processed_csv = processed_csv

    ## Load the data first and then process it 
    def load_and_process(self):
        df = pd.read_csv(self.original_csv, encoding="utf-8", on_bad_lines='skip').dropna()
        required_cols = {'Name', 'Genres', 'sypnopsis'}
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"The following columns are missing: {missing}")

        ## Combine the required columns into a single column
        df['combined_info'] = (
            "Title: " + df['Name'] + " Overview: " + df['sypnopsis']+ " Genres: " + df['Genres']
        )

        ## Save the processed data to a new CSV file
        df[['combined_info']].to_csv(self.processed_csv, index=False, encoding="utf-8")

        return self.processed_csv