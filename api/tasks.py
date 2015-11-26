from celery import Celery
from model import Wall, Post, WalledModel
from wallizers import TextWallizer, ImageWallizer

AWS_ACCESS_KEY = "YOUR_KEY_GOES_HERE"
AWS_SECRET_ACCESS_KEY = "YOUR_KEY_GOES_HERE"


import boto

def upload_s3(filename):
	#upload to S3
	s3 = boto.connect_s3(aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
	bucket_name = 'walled'
	bucket = s3.get_bucket(bucket_name)
	key = bucket.new_key(filename)
		#key.set_contents_from_string("Hello World!")
	key.set_contents_from_filename('../tmp/'+filename)
	key.make_public()
	url = 'http://'+bucket_name+'.s3-eu-west-1.amazonaws.com/'+filename
	return url

app = Celery('tasks', broker="redis://localhost")

@app.task
def wallize(wall_id, post_id):
	wm = WalledModel()
	post = wm.get_post(post_id)
	wall = wm.get_wall(wall_id)
	filename = None
	if post.type == 'text':
		wl = TextWallizer(wall=wall, post=post)
		filename = wl.wallize()
	elif post.type == 'image':
		wl = ImageWallizer(wall=wall, post=post)
		filename = wl.wallize()

	if filename != None:
		url = upload_s3(filename)
		post.url = url
		post.status = 'READY'
	else:
		post.status = 'ERROR'		
	wm.update_post(post)
	return post_id