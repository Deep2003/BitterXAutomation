from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import argparse

# Function to set up the webdriver and open the webpage
def setup():
    """
    Initializes the WebDriver and opens the target URL.
    Returns:
        WebDriver object: An instance of the Chrome WebDriver.
    """
    driver = webdriver.Chrome()  # Initialize Chrome WebDriver
    driver.get("https://mdl.shsmu.edu.cn/BitterX/module/mainpage/mainpage.jsp")  # Navigate to the website
    return driver


# Function to close the WebDriver session
def teardown(driver):
    """
    Closes the WebDriver session.
    Args:
        driver: The WebDriver instance to be closed.
    """
    driver.quit()  # Close the WebDriver session


# Function to scrape data for a given SMILES string
def scrape(smiles):
    """
    Scrapes data from the webpage based on the provided SMILES string.
    Args:
        smiles (str): The SMILES representation of a chemical compound.
    """
    job_name = "Job"  # Placeholder job name

    try:
        # Find the input fields and buttons on the webpage
        job_name_input = driver.find_element(by=By.ID, value="jobName")
        smiles_input = driver.find_element(by=By.ID, value="smilesText")
        run_button = driver.find_element(by=By.ID, value="smilesRun")

        # Input job name and SMILES value, then click the run button to run job
        job_name_input.send_keys(job_name)
        smiles_input.send_keys(smiles)
        run_button.click()

        # Find and click "view job" button to navigate to next page
        view_job_button = driver.find_element(
            by=By.ID, value="jobInfoWindow").find_element(
            by=By.ID, value="ext-gen114").find_elements(
            by=By.CSS_SELECTOR, value="button")[1]  # Second button in the list
        view_job_button.click()

        # Locate the button for checking the result
        button = driver.find_element(
            by=By.XPATH,
            value="/html/body/div[1]/div[2]/div/div/div/div/div/div[1]/div/div/div/div[2]/div/div/div/div/div/div/div[2]/div/div[1]/div[2]/div/div/table/tbody/tr/td[8]/div/input")

        # If an error occurred for this job, print the error message and return
        if 'Error' in button.accessible_name:
            print(button.text)
            return

        # Check if the compound is bitter
        is_bitter = driver.find_element(
            by=By.XPATH,
            value="/html/body/div[1]/div[2]/div/div/div/div/div/div[1]/div/div/div/div[2]/div/div/div/div/div/div/div[2]/div/div[1]/div[2]/div/div/table/tbody/tr/td[7]/div/span").text.strip()

        if is_bitter == "Yes":  # If the compound is bitter, proceed to extract data
            button.click()  # Click the button to reveal more information
            receptor_list = driver.find_element(
                by=By.ID, value="ext-gen123").find_elements(
                by=By.CSS_SELECTOR, value="tbody")  # Extract receptor list

            tmp_list = []  # Temporary list to store receptor data

            # Loop through each receptor and extract bitter ID and probability
            for i in range(len(receptor_list)):
                # Find bitter ID using dynamic XPath
                tmp_xpath = f"/html/body/div[1]/div[2]/div/div/div/div/div/div[1]/div/div/div/div[2]/div/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/div/div[1]/div[2]/div/div[{i + 1}]/table/tbody/tr/td[3]/div/a/span"
                bitter_id = driver.find_element(by=By.XPATH, value=tmp_xpath).text.strip()

                # Find probability using dynamic XPath
                tmp_xpath = f"/html/body/div[1]/div[2]/div/div/div/div/div/div[1]/div/div/div/div[2]/div/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/div/div[1]/div[2]/div/div[{i + 1}]/table/tbody/tr/td[8]/div/span"
                probability = driver.find_element(by=By.XPATH, value=tmp_xpath).text.strip()

                # Add new columns to DataFrame if not already present
                if bitter_id not in df.columns:
                    df[bitter_id] = 'NA'  # Set default value to 'NA'

                # Store the probability value for the given SMILES
                df.loc[df["SMILES"] == smiles, bitter_id] = probability

            # Go back to the main page
            driver.back()

    except NoSuchElementException:
        # In case of an element not found, try to go back and scrape again
        driver.back()
        scrape(smiles)


# default files
input_file = "input.csv"
output_file = "output.csv"

# Initialize command line parser
parser = argparse.ArgumentParser()

# Add optional arguments
parser.add_argument("-i", "--Input", help = "Input File")
parser.add_argument("-o", "--Output", help = "Output File")

# Read arguments from command line
args = parser.parse_args()

# Parse arguments and assign files accordingly
if args.Input:
    input_file = args.Input
    print("Input File: % s" % args.Input)
if args.Output:
    output_file = args.Output
    print("Output File: % s" % args.Output)

# Read the input data from a CSV file
df = pd.read_csv(input_file)

# Initialize the WebDriver and configure timeout
driver = setup()
driver.implicitly_wait(60)  # Set implicit wait to handle slow page loads and job runtime

# Loop through each row in the input DataFrame and scrape data
for i, row in df.iterrows():
    print(i + 2)  # Print row index for progress tracking
    scrape(df.loc[i].iloc[1])  # Scrape for the SMILES value in the current row

teardown(driver)  # Close the WebDriver session
df.to_csv(output_file, index=False)  # Save the scraped data to CSV without the index column
