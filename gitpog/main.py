import requests
import optparse
import urllib.parse
import sys
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from termcolor import colored
from time import sleep
a=0
deprecation_count=1
def makerequest(equery):
    result=[]
    global GITHUB_API_TOKEN
    global language
    global deprecation_count
    token=GITHUB_API_TOKEN.strip()
    if(deprecation_count%10==0):
        sleep(10)
    if(language!=None):
        response=requests.get(f'https://api.github.com/search/code?q={equery}+language:{language}',headers={'Authorization':'token '+token})
    else:
        response=requests.get(f'https://api.github.com/search/code?q={equery}',headers={'Authorization':'token '+token})
    if(response.status_code==403):
        print('API search has been blocked by github wait for sometime')
        sleep(10)
    if(response.status_code==200):
        for i in response.json()['items']:
            result.append(i['html_url'])
        deprecation_count+=1
    else:
        print(response.text)
    return (equery,result)

parser=optparse.OptionParser(description='Gitpog is a tool which tries to do github dorking')
parser.add_option('-d',dest='target',help='Specify the target to dork (either a domain or target keyword)')
parser.add_option('-t',dest='token',help='Github token')
parser.add_option('-l',dest='lang',help='Language to search (like ruby)')
parser.add_option('-w',dest='wordlist',help='Wordlist containing a list of keywords',default='./wordlists/keywords.txt')
parser.add_option('-k',dest='keyword',help='Specific keyword u want to search')
parser.add_option('-o',dest='outputfile',help='Output to a file')
#parser result

presult,dummy=parser.parse_args()
if(presult.target==None):
    print('Needs a target to dork')
    sys.exit()
if(presult.token==None):
    print('Needs a github api token to run authenticated search')
    sys.exit()
if(presult.outputfile!=None):
    outfile=open(presult.outputfile,'a')
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
    filecontents=[urllib.parse.quote('"'+presult.target+'" '+i.strip('\n')) for i in f]
    #result=tpool.map(makerequest,filecontents)
    results=map(lambda x:tpool.submit(makerequest,x),filecontents)
    '''tpool.join()
    for f in result:
        if len(f)!=0:
            word,links=f
            print(colored(f'Results for the query {word}','green'))
            for link in links:
                print(colored(link,'blue'))
    '''
    '''
    for result in concurrent.futures.as_completed(results):
        query,links=result.result()
        if links!=[]:
            word=urllib.parse.unquote(query).strip(presult.target)
            print(colored(f'Results for the query {word}','green'))
            for link in links:
                print(colored(link,'blue'))
    '''    
    for word in filecontents:
            word,links=makerequest(word)
            print(colored('Results for the query ' +urllib.parse.unquote(word),'green'))
            print(links)
            if(a==1 and links!=[]):
                    outfile.write('Results for the query '+urllib.parse.unquote(word)+'\n')
                    outfile.write('\n'.join(links))            

    