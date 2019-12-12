NLP Project

For this project, we will be scraping data from GitHub repository README files. The goal will be to build a model that can predict what programming language a repository is, given the text of the README file.

We choose to search for the most popular repositories that focus on completing the Advent of Code challenges.

We organize our findings and anlysis into a jupyter notebook called final.ipynb


Acquisition + Preparation

For this project, we build a dataset yourself. We do this by web scraping a list of Github repositories and writing the python code necessary to extract the text of the README files and the primary programming language of the repository.
Our data includes 276 unique repositories which encompass over 20 programming languages. 


Exploration

During the exploration, we answer the following questions:
What are the most common words in READMEs?
What does the distribution of IDFs look like for the most common words?
Does the length of the README vary by programming language?
Do different programming languages use a different number of unique words?


Modeling


In modeling, we transform our dataframe into a form that can be used in machine learning models.
We fit several different models  using the TF-IDF values for each).
Lastly, we build a function that takes in the text of a README file, and tries to predict the programming language.


*Required to Recreate our Findings:*
1. Final.ipynb and python files included within this repository
2. A file called env.py that contains the following information:
    - github_token = **YOUR_GITHUB_TOKEN_AS_STRING**
    - github_username = **YOUR_USER_NAME_AS_STRING**