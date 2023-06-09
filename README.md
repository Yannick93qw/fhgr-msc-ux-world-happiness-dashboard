# FHGR World Happiness Dashboard 
A dashboard that uses the data from the World Happiness Report.
The data can be found [here](https://www.kaggle.com/datasets/usamabuttar/world-happiness-report-2005-present).

The dashboard was programmed using the Python Programming Language and the following packages :snake:

- [Dash](https://dash.plotly.com/)
- [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)
- [Pandas](https://github.com/pandas-dev/pandas)
- [PyCountry](https://github.com/flyingcircusio/pycountry)

## :warning: Install required Packages
It is good practice to create a `virtual environment` first. In order to do that simply run

```bash
python -m venv .venv
```

To acticate the environment run the following code

`Mac OS or Linux`

```bash
source .venv/bin/activate.sh
```

`Windows`

```bash
.venv/bin/Activate.ps1
```

In order to install the required python packages simple run the following command:

```bash
pip install -r requirements.txt
```

Note that in order to use the Jupyter Notebooks located in `jupyter-notebook` please make sure you separately install the package with:
```bash
pip install notebook
```

I did not include this in the requirements file as this would make the Heroku image unnecessarily large. Furthermore Jupyter Notebook is not required in order to run the Dashboard itself.

## :nail_care: A word about data cleaning 
As mentioned above the World Happiness Report Data set was used. In order to effectively use the dataset in the dashboard a few "cleaning meassures" had to be done:
* Remove any countries which do not have a valid ISO Country Code (the choropleth map needs valid ISO Country codes)
* Fill in missing values via interpolation
* Precalculate the ranking of each country for each year and each feature in comparison to the rest. This would probably be expensive at runtime so we did precalculate these values.
* Remove unnecessary columns
* Rename columns
* Add a iso specific country code for each country with the help of the PyCountry Library

The entire data cleaning is done via the `data_cleaning.py` file. It can simply be run via

```bash
python data_cleaning.py
```

It will generate a `data_cleaned.csv` file which is used for the dashboard. 

## Run the Application locally
The application can be run by typing the following command inside a terminal:

```bash
python main.py
```

## :rocket: See it in action 
The application is also live on Heroku under the following [URL](https://fhgr-msc-dv-world-happiness-c6fabbfb0ded.herokuapp.com/).
This was accomplished with this wonderful guide [here](https://towardsdatascience.com/deploying-your-dash-app-to-heroku-the-magical-guide-39bd6a0c586c).
