import requests
from bs4 import BeautifulSoup
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import re

#user response
def checkWithUser():
    user_input=input('Continue[Y/n]:~') or 'y'
    if(user_input.lower()!='y'):
        print('\nQuitting program...')
        time.sleep(1)
        # exit()
        input('paused?')
    print('\n')
#end of user response

#URL validator framework
def is_valid_url(url):
    pattern = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}|[A-Z0-9-]{2,})|' # domain...
        r'localhost|' # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(pattern, url) is not None
#end of validator

#loading framework
l_tracker=0
loading_limit=40
def loadingBar(current,total,label):
    global l_tracker,loading_limit
    def clear_last_line():
        print('\033[A\033[K', end='')
    if(l_tracker!=0):
        clear_last_line()
    l_tracker=1
    stan_value=((current*loading_limit)//total)
    if(stan_value==loading_limit):
        l_tracker=0
    print(f"{label}:[{'#'*stan_value}{' '*(loading_limit-stan_value)}]{stan_value*100/loading_limit}%")
#end of loading framework

#user inputs
print('\nApple Music to Spotify Playlist converter by CipherKill\n')
print('*'*50)
print("NOTE: You'll be prompted to login to spotify for \n\tthe program to create playlist in your account.\n")
print('*'*50)
print('\n')
apple_playlist_link=str(input('[1]Enter link to Apple Music Playlist:~'))
playlist_name=str(input("[2]Enter new Playlist name for Spotify:~"))

#userinput validation
if(is_valid_url(apple_playlist_link)==False):
   raise Exception('Invalid URL please run program again.')

#main program
response=requests.get(apple_playlist_link)
memory=[]

print('-'*50)
if(response.status_code != 200):
    raise Exception('Invalid status code')
else:
    soup=BeautifulSoup(response.content,'html.parser')
    script_tag=soup.find('script',id='serialized-server-data')
    if script_tag:
        json_raw=script_tag.string
    
        jsondata=json.loads(json_raw)
        targetData=jsondata[0]['data']['sections'][1]['items']

        print(f'\nDetected Song Count: {len(targetData)}') #log line
        checkWithUser()

        count=0 #loading
        # print('\n')#loading
        for data in targetData:
            count+=1 #loading
            loadingBar(count,len(targetData),'Scraping')#loading
            memory.append({"songname":data['title'],"artist":data['subtitleLinks'][0]['title']})
    else:
        raise Exception('Issue scraping from apple music')
print('-'*50)
#at this point the memory is populated
#adding to spotify

sp=spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="Put_client_id_here",
    client_secret="Put_client_secret_here",
    redirect_uri="http://localhost:8080",
    scope="playlist-modify-public"
))

songs=[f"{dat['songname']} {dat['artist'][:3]}" for dat in memory]

track_ids=[]
total_tracks=len(songs)#loading
current_track=0#loading
for song in songs:
    current_track+=1
    loadingBar(current_track,total_tracks,'Fetching Tracks')#loading
    result=sp.search(q=song,type='track',limit=1)
    if result['tracks']['items']:
        track_ids.append(result['tracks']['items'][0]['id'])

print(f"Found {len(track_ids)}/{len(songs)}")
# checkWithUser()

print('-'*50)
user_id=sp.current_user()['id']
playlist=sp.user_playlist_create(user=user_id,name=playlist_name,public=True)

if track_ids:
    batch_size=50
    total_loop_count=(len(track_ids)//50)+1
    count=0
    for i in range(0,len(track_ids),batch_size):
        time.sleep(1)
        count+=1
        loadingBar(count,total_loop_count,'Creating Playlist')#loading
        track_batch=track_ids[i:batch_size+i]
        sp.playlist_add_items(playlist_id=playlist['id'],items=track_batch)
    print("Playlist created and populated!")
else:
    print("No tracks found, failed to create playlist\n") 
print('-'*50)
input('\n Press [ENTER] to close program gracefully...')
    #check how much times does the for loop runs



    
        
