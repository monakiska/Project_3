# Engeto Academy - Elections Scraper Project

Monika Kišková  
stastnamona@seznam.cz

### Project description
The goal of this project is extracting results of 2017 parliamentary elections. The results are available [here](https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ).

### Libraries instalation
All libraries that are used in the code are saved in file requirements.txt. It is recommended to use virtual environment to install the libraries and install them as showed below:  
`$ pip install -r requirements.txt`

### Project execution
For execution of the code in file main.py it is necessary to submit 2 arguments to command line. First argument is url to a chosen territorial unit and second argument is required name of csv file as showed below:  
`python main.py <specific url> <csv file name>`  
Afterwords results are downoaded to the csv file with the required name.

### Example
Voting results for Brno-mesto district:  
1. argument: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=11&xnumnuts=6203
2. argument: vysledky_brno_mesto.csv

Program execution:  
`python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=11&xnumnuts=6203" vysledky_brno_venkov.csv`

Download progress:  
`Downloading data from: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=11&xnumnuts=6203`  
`Downloading completed. Saved as vysledky_brno_venkov.csv (number of rows: 187).`
