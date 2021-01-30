import requests
import optparse
import urllib.parse
import sys
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from termcolor import colored
from time import sleep
import os
a=0
filter=0
deprecation_count=1
def makerequest(word):
    result=[]
    global GITHUB_API_TOKEN
    global language
    equery=urllib.parse.quote('"'+presult.target+'" '+word.strip('\n'))
    global deprecation_count
    token=GITHUB_API_TOKEN.strip()
    if(deprecation_count%10==0):
        sleep(15)
    if(language!=None):
        response=requests.get(f'https://api.github.com/search/code?q={equery}+language:{language}&per_page=100',headers={'Authorization':'token '+token})
    else:
        response=requests.get(f'https://api.github.com/search/code?q={equery}&per_page=100',headers={'Authorization':'token '+token})
    if(response.status_code==403):
        print('API search has been blocked by github wait for sometime')
        sleep(10)
        makerequest(equery)
    if(response.status_code==200):
        for i in response.json()['items']:
            result.append(i['html_url'])
        deprecation_count+=1
    else:
        print(response.text)
    return (word,result)

parser=optparse.OptionParser(description='Gitpog is a tool which tries to do github dorking')
parser.add_option('-d',dest='target',help='Specify the target to dork (either a domain or target keyword)')
parser.add_option('-t',dest='token',help='Github token')
parser.add_option('-l',dest='lang',help='Language to search (like ruby)')
parser.add_option('-w',dest='wordlist',help='Wordlist containing a list of keywords',default='./wordlists/keywords.txt')
parser.add_option('-k',dest='keyword',help='Specific keyword u want to search')
parser.add_option('-o',dest='outputfile',help='Output to a file')
parser.add_option('-r',dest='repo',help='Target github for better filtering of results')
#parser result

presult,dummy=parser.parse_args()
if(presult.target==None):
    print('Needs a target to dork')
    sys.exit()
if(presult.token==None):
    print('Needs a github api token to run authenticated search')
    sys.exit()
if(presult.outputfile!=None):
    os.system('mkdir '+presult.outputfile)
    a=1    


GITHUB_API_TOKEN=presult.token
language=presult.lang
#Search for a specific keyword
if(presult.keyword!=None):
    query=urllib.parse.quote(f'"{presult.target}" {presult.keyword}')
    makerequest(query)
else:
    wordlist=presult.wordlist
    tpool=ThreadPoolExecutor(max_workers=1)
    f=open(wordlist,'r').readlines()
#This line makes the github code request
    results=map(lambda x:tpool.submit(makerequest,x),f)
    for result in concurrent.futures.as_completed(results):
        word,links=result.result()
        #Filter results based on repos
        if presult.repo!=None:
            filtered_links=[]
            for link in links:
                if(presult.repo in link):
                    filtered_links.append(link)
            links=filtered_links

        #word=word.strip('\n').strip('=').strip('-')
        word=word.translate(word.maketrans('&=-\?$\n#','        ')).strip(' ')
        if links!=[]:
            print(colored(f'Results for the keyword {word}','green'))
            if(a==1 and links!=[]):
                    outfile=open(presult.outputfile+f'/{word}','w')
                    outfile.write(colored('\nResults for the query '+urllib.parse.unquote(word)+'\n','green'))
                    outfile.write(colored('\n'.join(links),'blue'))

            for link in links:
                print(colored(link,'blue'))        

    