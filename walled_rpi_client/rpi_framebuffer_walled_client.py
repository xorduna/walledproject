import requests, json, shutil, time, time, sys
from testfbi import pyscope

WALLED_SERVER = sys.argv[1]
WALL_ID = sys.argv[2]
url = WALLED_SERVER+'/walls/'+str(WALL_ID)+'/posts'
scope = pyscope()
last_content_id = None
while True:
	try:
		r = requests.get(url)
		posts = r.json()
		for p in posts:
			if last_content_id == None:
				last_content_id = p['id']

			#get the last content that is ready
			if p['status'] == 'READY' and last_content_id < p['id']:
				print p['id'], p['status'], p['url']
				tmp_path = 'tmp_file'
				r = requests.get(p['url'], stream=True) #download content
				if r.status_code == 200:
					with open(tmp_path, 'wb') as f:
						r.raw.decode_content = True
						shutil.copyfileobj(r.raw, f)

				scope.show_image(tmp_path)	#show content using pygame

				last_content_id = p['id']
				print 'last content', last_content_id
				time.sleep(0.1)
			
			if p['status'] == 'ERROR':
				last_content_id = p['id']
				print 'last content', last_content_id

	except requests.exceptions.ConnectTimeout:
		print 'error connecting. retrying'
	time.sleep(0.1)

		

