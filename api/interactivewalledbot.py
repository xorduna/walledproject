# -*- coding: utf-8 -*-

import telegram
import time
import requests, shutil
import random, string, json
import redis

def hash_file():
    return ''.join(random.choice(string.ascii_letters) for x in range(5))

TELEGRAM_TOKEN= 'YOUR_KEY_GOES_HERE'
WALLED_SERVER = 'http://localhost:5000'


bot = telegram.Bot(token=TELEGRAM_TOKEN)
redis = redis.StrictRedis(host='localhost', port=6379)	
last_update = redis.get('bot:last_update')

while True:    
    if last_update == None:
        updates = bot.getUpdates()
    else:
        updates = bot.getUpdates(offset=last_update)

    for u in updates:
        user = u.message.from_user.first_name
        message = u.message.text
        chat_id = u.message.from_user.id

        if not redis.hexists('bot:session:'+str(chat_id), 'user'):
        	#start session
        	print 'new session!!!'
        	redis.hset('bot:session:'+str(chat_id), 'user', user)

        wall_id = None
        #check for commands
        words = message.split(' ')
        if words[0] == '/start':
            print 'COMMAND START'
            if len(words) > 1:
                wall_name = words[1]
                #find wall name
                wall_id = wall_name
                redis.hset('bot:session:'+str(chat_id), 'wall_id', wall_id)
                bot.sendMessage(chat_id=chat_id, text="Welcome to our LED Wall! You can start sending text or images right now to wall " + str(wall_id))


        elif words[0] == '/wall' and len(words) == 2:
            print 'COMMAND JOIN WALL'
            wall_name = words[1]
            #find wall name
            wall_id = wall_name
            redis.hset('bot:session:'+str(chat_id), 'wall_id', wall_id)
            



            bot.sendMessage(chat_id=chat_id, text="You are now connected to wall "+str(wall_name))


        else:

            if not redis.hexists('bot:session:'+str(chat_id), 'wall_id'):
            	print 'not associated with any wall'
            	bot.sendMessage(chat_id=chat_id, text="You are not connected to any wall! To connect to a wall type: /wall WALL_NAME where WALL_NAME is the name you will find below the wall.")
            else:
            	wall_id = redis.hget('bot:session:'+str(chat_id), 'wall_id')
            	print 'user connected to wall: ', wall_id
            if wall_id != None:
                url = WALLED_SERVER + '/walls/'+str(wall_id)+'/posts'

                post = {'user': user, 'text': u.message.text }

                if len(u.message.photo) > 0:
                    post['type'] = 'image'
                    images = u.message['photo']
                    for im in images:
                        print bot.getFile(im['file_id'])
                    im = images[-1] #get the last image
                    file_url = bot.getFile(im['file_id'])['file_path'] #, im['width'], im['height']
                    filename = file_url.split('/')[-1]
                    r = requests.get(file_url, stream=True)
                    path = '../tmp/'+hash_file()+'_'+filename
                    if r.status_code == 200:
                        with open(path, 'wb') as f:
                            r.raw.decode_content = True
                            shutil.copyfileobj(r.raw, f)
                    r = requests.post(url, data={'data': json.dumps(post)}, files = {'file': open(path, 'rb')})

                else:
                    post['type'] = 'text'
                    r = requests.post(url, data={'data': json.dumps(post)} )
                    print r.status_code

                print post



    	print last_update


    	last_update = u.update_id + 1
    	redis.set('bot:last_update', last_update)
    time.sleep(1)



