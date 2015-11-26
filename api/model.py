import redis
import json

class Post:

	def __init__(self, type='', content_local_path='', user='', id=None, status='PENDING', url=None, text=''):
		self.id = id
		self.type = type
		self.text = text
		self.url = url
		self.user = user
		self.content_local_path = content_local_path
		self.status = status

	def to_json(self):
		return json.dumps({'id': self.id, 'url': self.url, 'type': self.type, 'content_local_path': self.content_local_path, 'status': self.status, 'user': self.user, 'text': self.text})

class Wall:

	def __init__(self, id=None, alias='', name='', height=32, width=32, token=''):
		self.id = id
		self.height = height
		self.width = width
		self.alias = alias
		self.name = name
		self.token = token

	def to_json(self, token=True):
		if token:
			return json.dumps({"id": self.id, "alias": self.alias, "height": self.height, "width": self.width, "name": self.name, "token" : self.token})
		else:
			return json.dumps({"id": self.id, "alias": self.alias, "height": self.height, "width": self.width, "name": self.name })
		

class WalledModel:
	def __init__(self, db=0):
		self.r = redis.StrictRedis(host='localhost', port=6379, db=db)		

	def create_post(self, post):
		post_id = self.r.incr('post_ids')
		post.id = post_id
		self.r.rpush('posts_list', post.id) 
		self.r.set('posts:'+str(post.id), post.to_json())
		return post

	def get_post(self, post_id):
		post = json.loads(self.r.get('posts:'+str(post_id)))
		p = Post(id = post['id'], type=post['type'], user=post['user'], status=post['status'], content_local_path=post['content_local_path'], url=post['url'], text=post['text'])
		return p

	def update_post(self, post):
		self.r.set('posts:'+str(post.id), post.to_json())
		return post

	def create_wall(self, wall):
		wall_id = self.r.incr('wall_ids')
		wall.id = wall_id
		self.r.rpush('walls_list', wall.id)
		self.r.set('walls:'+str(wall.id), wall.to_json())
		self.r.set('walls_alias:'+str(wall.alias), wall.id)
		self.r.set('tokens:'+str(wall.token), wall.id)
		self.r.set('tokens_wall:'+str(wall.token), wall.id)

	def get_wall(self, wall_id):
		wall = json.loads(self.r.get('walls:'+str(wall_id)))
		w = Wall(id = wall['id'], height=wall['height'], width=wall['width'], name=wall['name'], alias=wall['alias'], token=wall['token'])
		return w

	def get_walls(self):
		walls_list = self.r.lrange('walls_list', 0, -1)
		walls = []
		print walls_list
		for wall_id in walls_list:

			raw_wall = self.r.get('walls:'+str(wall_id))
			if raw_wall != None:
				wall = json.loads(raw_wall)
				walls.append(wall)
		return walls

	def add_post_to_wall(self, wall_id, post_id):
		self.r.rpush('walls_posts:'+str(wall_id), post_id)

	def get_wall_posts(self, wall_id):
		return self.r.lrange('walls_posts:'+str(wall_id), 0, -1)

	def update_wall(self, wall):
		self.r.set('walls:'+str(wall.id), wall.to_json())
		self.r.set('walls_alias:'+str(wall.alias), wall.id)
		#remove old token
		old_token = self.r.get('tokens_wall_id:'+str(wall.id))
		if old_token != None:
			self.r.delete('tokens:'+old_token)
		self.r.set('tokens:'+str(wall.token), wall.id)
		self.r.set('tokens_wallid:'+str(wall.id), wall.token)
		return wall

	def delete_wall(self, wall_id):
		#remove key
		self.r.delete('walls:'+str(wall_id))
		#remove from listing
		self.r.lrem('walls_list', 1, wall_id)
		#we should also find the token and remove it
		token = self.r.get('tokens_wallid:'+str(wall_id))
		if token != None:
			self.r.delete('tokens:'+str(token))
		self.r.delete('tokens_wallid:'+str(wall_id))
		return True

	def get_wall_from_alias(self, wall_alias):
		return self.r.get('walls_alias:'+str(wall_alias))

	def check_user(self, user, password):
		return self.r.get('users:'+user) == password
		





