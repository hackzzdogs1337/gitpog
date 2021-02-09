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
    global presult
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
        print(response.status_code)
    #Filter results based on repos
    if(presult.repo!=None and response.status_code==200):
        filtered_links=[]
        indices=[]
        repo_names=[i['repository']['full_name'].split('/')[0] for i in response.json()["items"]]
        for repo in repo_names:
            if(presult.repo == repo):
                    indices.append(repo_names.index(repo))
        repo_results=[result[i] for i in indices]
        if(presult.fu==None):
            return(word,repo_results)
        else:
            result=repo_results
    #Filter based on user of the target organisation    
    '''if(presult.fu!=None and response.status_code==200):
        indices=[]
        users_url=[ i['repository']['owner']['url'] for i in response.json()["items"]]
        #Make request to user api endpoint to get organisation name
        userss_json=list(map(lambda x: requests.get(x,headers={'Authorization':'token '+token}).json()['company'],users_url))
        users_json=[i.strip('@') for i in userss_json if i]

        print(users_json)
        for user_json in users_json:
                if(user_json!=None):
                    if(presult.target.lower()==user_json.lower()):
                        indices.append(users_json.index(user_json))
        user_filtered_results=[result[i] for i in indices]
        return(word,user_filtered_results)'''
        
    return (word,result)

parser=optparse.OptionParser(description='Gitpog is a tool which tries to do github dorking')
parser.add_option('-d',dest='target',help='Specify the target to dork (either a domain or target keyword)')
parser.add_option('-t',dest='token',help='Github token')
parser.add_option('-l',dest='lang',help='Language to search (like ruby)')
parser.add_option('-w',dest='wordlist',help='Wordlist containing a list of keywords',default='./wordlists/keywords.txt')
parser.add_option('-k',dest='keyword',help='Specific keyword u want to search')
parser.add_option('-o',dest='outputfile',help='Output to a file')
parser.add_option('-r',dest='repo',help='Filter by target home github repo')
#Yet to be developed
#parser.add_option('--userenum',dest='users',help='This flag will make the tool to search these keywords on people who work on the target organisation obtained from the initial gitpog result')
#parser.add_option('-u',dest='fu',help='Filter the results based on people who work in the target organisation specify "y" if you want(this will take a bit of time:))')
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
        #word=word.strip('\n').strip('=').strip('-')
        word=word.translate(word.maketrans('&=-\?$\n','       ')).strip(' ')
        if links!=[]:
            print(colored(f'Results for the keyword {word}','green'))
            if(a==1 and links!=[]):
                    outfile=open(presult.outputfile+f'/{word}','w')
                    outfile.write(colored('\nResults for the query '+urllib.parse.unquote(word)+'\n','green'))
                    outfile.write(colored('\n'.join(links),'blue'))

            for link in links:
                print(colored(link,'blue'))        

    