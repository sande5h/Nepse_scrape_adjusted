# NepseAlpha Data Scraper

This Python script is designed to scrape stock market data from [NepseAlpha](https://nepsealpha.com/). It uses Selenium to automate web browsing and extract data such as stock symbols, historical prices, and market capitalization. The data is then saved in CSV files for further analysis.

## Features

- **Scrape Stock Symbols**: Fetches the list of traded stocks from NepseAlpha.
- **Historical Data Extraction**: Downloads historical stock data for each symbol.
- **Data Backup**: Automatically backs up the downloaded data.
- **Directory Management**: Initializes necessary directories and cleans up old data.

## Prerequisites

Before running the script, ensure you have the following installed:

- Python 3.x
- ChromeDriver (compatible with your Chrome version)
- Required Python packages (listed in `requirements.txt`)

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/nepsealpha-scraper.git
   cd nepsealpha-scraper
   ```


2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Download ChromeDriver**:

    Download the appropriate version of ChromeDriver .
    Ensure the chromedriver executable is in your system's PATH or place it in the project directory.

## Usage

1. **Initialize Directories**:

The script will automatically create necessary directories (data, backup, response, symbols, index, backups_month, screenshots) if they don't exist.

2. **Run the Script**:
    ```bash
    python main.py
    ```

The script will:

- Scrape the list of traded stocks and save it to symbols/symbols.csv.

- Download historical data for each stock symbol and save it in the data directory.

- Backup the downloaded data to the backup directory.

- Perform monthly backups by moving the first backup of each month to the backups_month directory.

- Clean up old data from specified directories.

## Functions Overview

- ***check_for_symbols()***: Fetches the list of traded stocks from NepseAlpha and saves it to symbols/symbols.csv.

- ***historical_data(symbol, folder)***: Downloads historical data for a given stock symbol and saves it in the specified folder.

- ***main()***: Orchestrates the scraping process by calling check_for_symbols() and historical_data() for each symbol.

- ***fetch()***: Checks for new data and runs the main scraping function if new data is found.

- ***backup_data_folder(folder)***: Creates a zip backup of the data folder.

- ***unzip()***: Unzips the latest backup file.

- ***clean_dir(paths)***: Cleans up specified directories by removing their contents.

- ***init_dir()***: Initializes necessary directories.

- ***monthy_backup()***: Moves the first backup of each month to the backups_month directory.



## Notes

- Ensure you have a stable internet connection while running the script.

- The script may take some time to complete, depending on the number of symbols and the amount of data being scraped.

- Regularly check the screenshots directory for any errors captured during the scraping process.





## Disclaimer

This script is provided for educational and personal use only. The author is not responsible for any misuse of this script, including but not limited to:

- Use for commercial purposes.

- Violation of the terms of service of NepseAlpha or any other website.

-Any legal or financial consequences arising from the use of this script.



By using this script, you agree to use it at your own risk. The author is not liable for any damages or losses incurred as a result of using this script.

For any questions or issues, please open an issue on the GitHub repository.

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
