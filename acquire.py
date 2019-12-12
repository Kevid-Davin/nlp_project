###############################################################################
### pthon imports                                                           ###
###############################################################################

from os import path
from requests import get
from bs4 import BeautifulSoup
import os
import pandas as pd
import re

###############################################################################
### local imports                                                           ###
###############################################################################

import zachquire as zaq

def find_file(
    file_name='path/file.txt',
    cache=False,
    cache_age=None
    ):

    if cache==False:
        return None
    
    return path.exists(file_name)


def get_soup(
    url='https://github.com/search?o=desc&p=1&q=advent+of+code&s=stars&type=Repositories',
    headers={'User-Agent': 'Nothing suspicious'},
    file_name='soupfiles/gitsearch.txt',
    cache=False,
    cache_age=None,
    slurper='*'
):
    '''
    
    '''
    # if we already have the data, read it locally
    file_found = find_file(file_name=file_name, cache=cache, cache_age=cache_age)
    if file_found:
        with open(file_name) as f:
            return True, BeautifulSoup(f.read())

    # otherwise go fetch the data
    response = get(url, headers=headers)
    soup = BeautifulSoup(response.text)
    slurps = soup.select(slurper)
    if len(slurps) == 0:
        print('***** NO DATA RETURNED *****')
        return False, soup
    
    # save it for next time
    with open(file_name, 'w') as f:
        f.write(str(slurps[0]))
        if len(slurps)>1:
            for slurp in slurps[1:]:
#                 print(str(slurp))
                f.write('\n' + str(slurp))
        
    with open(file_name) as f:    
        soup = BeautifulSoup(f.read())
#     pd.to_csv(slurps, header=None, index=False)

    return True, soup


def soup_loop_gitsearch(
    df,
    page_beg=1,
    page_end=20,
    url='https://github.com/',
    adder_prepage='search?o=desc&',
    adder_postpage='&q=advent+of+code&s=stars&type=Repositories',
    headers={'User-Agent': 'Nothing suspicious'},
    directory='soupfiles/',
    file_name='gitsearch',
    file_suffix='.txt',
    cache=False,
    slurper='.repo-list-item a',
    print_it = False
):
    for page in range(page_beg, page_end+1):
        use_page = str(page)
        use_url = f'{url}{adder_prepage}p={use_page}{adder_postpage}'
        use_file = f'{directory}{file_name}{use_page:>02s}{file_suffix}'
        if print_it:
            print(f'use_page: {use_page:>2s}')
            print(f'use_url: {use_url}')
            print(f'use_file: {use_file}')
        slurped, soup = get_soup(
            url = use_url,
            file_name = use_file,
            cache = cache,
            slurper = slurper,
        )
        log_file = use_file if slurped else None
        loopdict = {
            'soup': [soup], 
            'page': [page], 
            'url': [use_url], 
            'file_name': [log_file]
        }
        df = df.append(pd.DataFrame.from_dict(loopdict), ignore_index=True)
    return df


def make_soup_gitsearch(
    page_beg=1, 
    page_end=20,
    headers={'User-Agent': 'Nothing suspicious'},
    adder_prepage='search?o=desc&',
    adder_postpage='&q=advent+of+code&s=stars&type=Repositories',
    directory='soupfiles/',
    file_name='gitsearch',
    file_suffix='.txt',
    cache=True,
    slurper='.repo-list-item a',
    print_it=False
):
    soup_df = pd.DataFrame([], columns=['soup','page','url','file_name'])
    soup_df = soup_loop_gitsearch(
        soup_df, 
        cache=True, 
        headers=headers,
        page_beg=page_beg, 
        page_end=page_end,
        adder_prepage=adder_prepage,
        adder_postpage=adder_postpage,
        file_name=file_name,
        file_suffix=file_suffix,
        slurper=slurper,
        print_it=print_it
    )
    return soup_df


def get_repo_urls_from_gitsearch(df, column='soup', reg_text=r'"url"\:"(.+?)"'):
    git_urls = []
    re_url = re.compile(reg_text)
    for soup in df.soup:
        git_urls.extend(re_url.findall(str(soup)))
    return list(set(git_urls))


def get_repos_from_url_list(url_list, reg_text=r'https\://github.com/(.+?)$'):
    re_repo = re.compile(reg_text)
    repo_list = []
    repo_check = [re_repo.findall(url)[0] for url in url_list]
    repo_list.extend(repo_check)
    repo_list.sort()
    return repo_list


def get_subrepos_from_readmes(
    repos=['Bogdanp/awesome-advent-of-code'],
    filepath="datafiles/xtrafile.json",
    reg_text=r'\(https\://github.com/(.+?)\)',
):
    zaq.scrape_github_data(repos=repos, filepath=filepath)
    git_df = pd.read_json(filepath).rename(columns={'repo':'repo_full'})
    git_readme = git_df.readme_contents[0]
    re_xtra = re.compile(reg_text)
    readme_urls = re_xtra.findall(git_readme)
    subrepos = [i.split('/')[0] + '/' + i.split('/')[1] for i in readme_urls]
    subrepos.sort()
    return subrepos


def merge_repo_list(repos=[], xtra_repos=[], remove_repos=[]):
    repos.extend(xtra_repos)
    repos = list(set(repos))
    for repo in remove_repos:
        if repo in repos:
            repos.remove(repo)
    repos.sort(key=str.lower)
    return repos


def scrape_github_data(repos=[], filepath="datafiles/data.json"):
    zaq.scrape_github_data(repos=repos, filepath=filepath)
    return True


def process_scraped_repos(filepath = "datafiles/data.json", remove_repos=[]):
    git_json = pd.read_json(filepath).rename(columns={'repo':'repo_full'})
    git_json=git_json[git_json.repo_full.isin(remove_repos)==False].dropna().reset_index().drop(columns='index')
    git_json['author'] = git_json.repo_full.apply(lambda x: x.split('/')[0])
    git_json['repo'] = git_json.repo_full.apply(lambda x: x.split('/')[-1])
    git_json['readme'] = git_json.readme_contents.str.lower()
    git_json['readme'] = [git_json.readme[i].replace(git_json.author[i].lower(), 'username') for i in range(0,len(git_json))]
    git_json['readme'] = [git_json.readme[i].replace(git_json.repo[i].lower(), 'reponame') for i in range(0,len(git_json))]

    return git_json


def output_processed_repos(git_df, output_file='datafiles/outdata.json'):
    git_df.drop(columns=['readme_contents']).to_json(output_file, orient = 'columns')
    json_chk = pd.read_json(output_file)
    return json_chk


if __name__ == '__main__':
    print('opened acquire')