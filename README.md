# BitterXAutomation
Python Web Scraping Program to Automate queries and results on BitterX website

@Authors: 
Deep Patel, Amritansh Ayachi

To utilize the program, you can add a csv file with name "input.csv" into the same directory as the main.py file. Upon succesful execution of the program, the directory will have a "output.csv" file with results of the queries. 

To utilize the program via command line with custom arguments, you can indicate -i INPUT, -o OUTPUT, and -t TIME in the command line. For example:
"main.py -i input.csv -o output.csv -t 90" would set input file as "input.csv", output file as "output.csv", and timeout as 90 seconds.

If no arguments are provided, the defaults will be set to "input.csv", "output.csv", and 900 seconds(15 minutes).
