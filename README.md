# espn-fantasy-football

This project seeks to provide analysis about ESPN Fantasy Football draft data based on the results of the season, using the ESPN Fantasy Football API (V3).

## Draft Results

### Overview

The *draftresults.py* function creates a spreadsheet containing a summary of the draft data and final results of a given season in a specified ESPN Fantasy Football League. This sheet has a section where pick ratings can be filled out and used to train an analysis model. The *draftanalysis.py* function uses the training data to create a model that evaluates a draft and outputs the results as an excel file.

### Getting Started

#### Command Line Arguments

Four command line arguments are needed for the *draftresults.py* function. The first two are cookies, which are required to access information for private leagues.

To access the cookies, in Chrome go to Settings -> Privacy and Security -> Site Settings -> Cookies and site data -> See all cookies and site data -> espn.com. Find the *espn_s2* and *SWID* cookies. These are the first two command line arguments.

The third command line argument is the League ID, which can be found simply by going to your league from the [ESPN Fantasy homepage](https://www.espn.com/fantasy/football/). From any page in your league, the url should have a *leagueId* value included within the url.

The fourth command line argument is Season ID, which is the year of the fantasy season that will be analyzed. Note that the season must be completed. Also it appears that there is no longer player information available for years before 2018, so the code will only work using 2018 or later.

The final function call will be in the form: python draftresults.py [*espn_s2 HERE*] [*SWID HERE*] [*LEAGUEID HERE*] [*SEASONID HERE*]

*Example:* python draftresults.py ABCDEFGHIJKLMNOPQRSTUVWXYZ%1%2%3%4%5%6%7%8%9%0 ABCD-EFG-HIJ-KLMN 12345 2019

No Command line arguments are needed for *draftanalysis.py*.

#### Additional Setup

I recommend creating and activating a Python virtual environment.

Install the necessary libraries by running *pip install -r requirements.txt* in the terminal.

### Code Details

#### Draft Results

This script, *draftresults.py* makes several GET requests using the ESPN Fantasy API. The URLs are defined in main, with different endpoints based on the data being obtained. 

The first request gets information on the teams that year, creating a key that links a Team ID to that team's name.

The second request creates a dictionary of all NFL players and relevant fantasy information from the given year, based on the results of the league and their scoring system. This function uses keys to link a Position ID to the position name (1 is QB and so on) and to link an NFL Team ID to the team name (1 is Atlanta and so on). These keys were created using the API data but are hard coded into the script, as they do not change.

The third request creates a dictionary of all players drafted in the fantasy league during that season, linking information about each players draft position with information obtained in the second request.

Once the requests are complete, the information is outputted to an Excel spreadsheet, identified by the League ID and year, created in the Drafts directory.

ESPN does not have information on this API, but details can be found [here](https://stmorse.github.io/journal/espn-fantasy-v3.html) and [here](https://www.reddit.com/r/fantasyfootball/comments/ct4hf3/new_espn_api/).

#### Draft Analysis

This script, *draftanalysis.py* trains a model based on sample training data and then applies that model to evaluate draft results.

The first step is reading in data provided to the model to train it. This data is located in the *Training* folder and can be created by generating a spreadsheet using *draftresults.py* and filling out ratings, or by using the sample training files provided in the directory. The script parses every excel file in the directory, gathering data specified by the *variables* array in main. The data is sorted by position (QB, RB, etc.) into a dictionary containing inputs (draft rank, final rank, total score, etc.) and output (pick rating).

Once the data is read in, the model is trained using the SVM feature of [Scikit-Learn](https://scikit-learn.org/stable/). A different model is generated for each position.

Once the models have been trained, they are capable of evaluating a draft based on the specified variables. Any excel file in the *Drafts* directory will be evaluated and the corresponding new excel file will be generated in the *Fitted* directory.

In addition to the original sheet containing a complete view of the draft data, additional sheets will be created for each individual fantasy team to provide an overview of that team's draft performance, showing their picks, color-coded on a gradient using Python's *colour* library based on the evaluation of that pick.

Lastly, analysis on overall trends in the data from the draft can be viewed in the *Leaderboards* sheet of the newly created excel file. This shows the overall draft performance of each fantasy team, as well as the ten best and worst picks from the draft.

### Acknowledgements

Thanks to Jack Conlin, Nick Goetz, Matt Muenchow, Hunter Zogg, Elliot Glaser, Jack Olmanson, Jack Rothstein, Ethan Edwards, Rowan Desjardins, Anirudh Panuganty, Cedar Palaia, Brent Prodahl, Joseph Larson, and Noah Rodriguez for their contributions to the training data and input to the model. This was a truly interactive process and this would not be what it is without their helpful feedback and suggestions.