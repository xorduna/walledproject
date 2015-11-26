
from PIL import Image, ImageDraw, ImageFont
import random, string
from model import Post, Wall, WalledModel
import boto

from PIL import ImageEnhance

import cuter

class PostWallizer:
	
	def __init__(self, wall, post):
		self.wall = wall
		self.post = post
		pass

	def hash_file(self):
		return ''.join(random.choice(string.ascii_letters) for x in range(20))

	def wallize():
		pass


class TextWallizer(PostWallizer):

	def wallize(self):
		txt = Image.new('RGBA', (self.wall.width, self.wall.height), (0,0,0))
		fnt = ImageFont.truetype('../fonts/BLOODY.TTF', 18)
		d = ImageDraw.Draw(txt)
		#color palette
		colors = [(255, 255,255), (255,255,0), (255,0,0), (0, 255, 255), (0, 0, 255), (0, 255, 0)]
		color = random.randint(0, len(colors))
		#method for cutting string into words to fit the width of the wall
		text = self.cut_string_words_pixels(self.post.text, draw=d, font=fnt, size=self.wall.width)
		#draw the text in the image and save it as PNG
		d.multiline_text((5,5), text, font=fnt, fill=(255,0,0), align='center')
		filename = self.hash_file() + '.png'
		txt.save('../tmp/' + filename, 'PNG')
		return filename


		#d.text((0,0), self.post.text, font=fnt, fill=colors[color])


	#this wallizer just gets text and converts to image
	def cut_string_words_pixels(self, s, draw, font, size):
		ns = ''
		words = s.split(' ')
		line = 0
		for w in words:
			ww = draw.textsize(w + ' ',font=font)[0]
			if line + ww < size:
				line = line + ww
				ns = ns + w + ' '
			else:
				line = ww
				#trim the last space
				ns = ns.strip() + '\n' + w + ' '
		return ns

class ImageWallizer(PostWallizer):

	def wallize(self):
		size = self.wall.width, self.wall.height
		print 'resising image to ', size
		filename = self.hash_file() + '.png'
		#bright = ImageEnhance.Brightness(im)
		#im = bright.enhance(0.5)
		#im.save('../tmp/' + filename, 'PNG')
		cuter.resize_and_crop(self.post.content_local_path, '../tmp/' + filename, size, crop_type='middle')
		return filename


