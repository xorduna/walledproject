from flask import Flask
from flask import request, render_template, redirect, url_for
from flask import session
from model import Wall, Post, WalledModel
from werkzeug import secure_filename

from tasks import wallize

import random, string
import json

import urllib

app = Flask(__name__)

#app['secret_key'] = 'this_is_secret'

@app.route("/")
def main():
    return redirect(url_for('admin_get_walls'))

#POST post to wall
@app.route("/walls/<int:wall_id>/posts", methods=["POST"])
def post_wall_post(wall_id):
	#get request data
	request_json = json.loads(request.form['data'])
	media_type = request_json['type']
	text = request_json['text']
	user = request_json['user']

	if media_type == 'image':			#it is an image that we should save
		file_hash = ''.join(random.choice(string.ascii_letters) for x in range(20))
		print request.files.keys()
		f = request.files['file']
		filename = '../tmp/' + file_hash + secure_filename(f.filename)
		f.save(filename)
	else:
		filename = None

	p = Post(text=text, type=media_type, content_local_path=filename, user=user)
	wm = WalledModel()						#small abstraction layer for redis

	post = wm.create_post(p)
	wm.add_post_to_wall(wall_id, post.id)	#store post in redis

	wallize.delay(wall_id, post.id)			#ask celery to create image from post
	
	return post.to_json()					#return


#GET wall from alias
@app.route('/walls/from_alias/<string:alias>', methods=['GET'])
def get_wall_from_alias(alias):
	wm = WalledModel()
	wall_id = wm.get_wall_from_alias(alias)
	if wall_id != None:
		return wm.get_wall(wall_id).to_json(token=False)
	else:
		return 'NOT FOUND'  #change for 404

#GET post from a wall
@app.route("/walls/<int:wall_id>/posts/<int:post_id>", methods=["GET"])
def get_wall_post(wall_id, post_id):
	return None

#GET all posts from a wall
@app.route("/walls/<int:wall_id>/posts", methods=["GET"])
def get_wall_post_list(wall_id):
	wm = WalledModel()
	posts = []
	post_ids = wm.get_wall_posts(wall_id)
	for id in post_ids[-5:]:
		posts.append(json.loads(wm.get_post(id).to_json()))
	return json.dumps(posts)

@app.route('/admin/walls')
def admin_get_walls():
	wm = WalledModel()

	walls = wm.get_walls()

	return render_template('walls.html', walls=walls)

@app.route('/admin/walls/<int:wall_id>', methods=["GET", "POST"])
def admin_get_wall(wall_id):
	wm = WalledModel()

	if request.method == 'GET':
		wall = wm.get_wall(wall_id)

		return render_template('wall.html', wall=wall)

	if request.method == 'POST':
		
		wall = wm.get_wall(wall_id)
		wall.name = request.form['name']
		wall.alias = request.form['alias']
		wall.width = int(request.form['width'])
		wall.height = int(request.form['height'])
		wall.token = request.form['token']
		wm.update_wall(wall)

		return redirect('/admin/walls')

@app.route('/admin/walls/new', methods=['GET', 'POST'])
def admin_new_wall():
	if request.method == 'GET':
		token = ''.join(random.choice(string.ascii_letters) for x in range(12))
		return render_template('newwall.html', token=token)
	if request.method == 'POST':
		name = request.form['name']
		alias = request.form['alias']
		height = int(request.form['height'])
		width = int(request.form['width'])
		token = request.form['token']

		w = Wall(name = name, alias=alias, height=height, width=width, token=token)
		wm = WalledModel()
		wm.create_wall(w)
		return redirect(url_for('admin_get_walls'))
		
	

@app.route('/admin/walls/delete/<int:wall_id>')
def admin_delete_wall(wall_id):

	wm = WalledModel()
	wm.delete_wall(wall_id)
	return redirect(url_for('admin_get_walls'))


@app.route('/login', methods = ['GET', 'POST'])
def login():
	if request.method == 'POST':
		wm = WalledModel()
		username = request.form['user']
		password = request.form['password']
		if wm.check_user(username, password):
			session['user'] = username
			return redirect(url_for('admin_get_walls'))
		else:
			return redirect(url_for('login'))
	else:
		return render_template('login.html')

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

