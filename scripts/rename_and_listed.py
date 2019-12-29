'''
Scripts: rename, listed, and postprocess
1. rename by using random name generator
2. origin_name (title) and new_name (string) recorded in `article_list`
3. postprocess, mature pandoc markdown file for publicaiton
'''

import sys, os, datetime, glob
import numpy as np
import shutil

now = datetime.datetime.now()

def gen_randome_name():
	import string, random
	letters = string.ascii_letters
	digits = string.digits
	filedate = str(now.year) + '-' + str(now.month) + '-' + str(now.day) + '-'
	return filedate + ''.join(random.sample(letters+digits, 16)) + '.md'


class md_processor():
	def __init__(self, md_filepath):
		self.out_md = []
		self.lines = open(md_filepath).readlines()
		self.header_end = self.head_thresh(self.lines)

		self.head_characters = ['layout', 'comments', 'title', 'date', 'categories', 'tags', 'description']
		self.out_header = {}
		for character in self.head_characters:
			if character == 'layout':
				self.out_header[character] = 'post'
			elif character == 'comments':
				self.out_header[character] = 'yes'
			elif character == 'date':
				self.out_header[character] = str(now.year) + '-' + str(now.month) + '-' + str(now.day)
			else:			
				self.out_header[character] = ''

		self.tail_jschar = ['js_sponsor_ad_area', 'js_more_read_area', 'js_like_educate']
		self.tail_start = self.tail_thresh()

	def head_thresh(self, lines, thresh_line=10):
		_htmp_ = []
		for i, line in enumerate(lines):
			if line == '---\n':
				_htmp_.append(i)
		if len(_htmp_) == 1:
			return thresh_line
		else:
			return _htmp_[-1]

	def tail_thresh(self):
		_ttmp_ = []
		for i, line in enumerate(self.lines[self.header_end:]):
			for tag in self.tail_jschar:
				if line.find(tag) > -1:
					_ttmp_.append(i)
		if len(_ttmp_) == 0:
			return len(lines)
		else:
			return min(_ttmp_)

	def header(self, end):
		for line in self.lines[0:end]:
			_ctns_ = line.strip().split(':')
			character = _ctns_[0]
			ctns = ''.join(_ctns_[1:])
			if character not in ['title', 'categories', 'tags', 'description']:
				continue
			else:
				self.out_header[character] = ctns

		self.out_md.append('---\n')
		for _head_character_ in self.out_header.keys():
			print(_head_character_, ': ', self.out_header[_head_character_])
			self.out_md.append(_head_character_+': '+self.out_header[_head_character_])
		self.out_md.append('---\n')
		self.out_md.append('\n')
		self.out_md.append('\n')

	def main(self, outpath):
		self.header(end=self.header_end)
		for line in self.lines[self.header_end:self.tail_start]:
			line = line.strip()
			if line.find('div') > -1:
				continue
			elif line.find('>') > -1:
				continue
			elif len(line) <= 3:
				continue
			else:
				_line_ = line.strip().split('{')[0].replace('[','').replace(']','').replace('{','').replace('}','')
				self.out_md.append(_line_)

		ofile = open(outpath, 'w')
		for obj in self.out_md:
			if obj.find('\n') == -1:
				obj += '\n'
			ofile.write(obj)
		ofile.close()
		


if __name__ == '__main__':

	article_list = sys.argv[1]
	origin_dir = sys.argv[2]
	out_dir = sys.argv[3]

	# print("??")
	artfile = open(article_list, 'a')

	for srcname in glob.glob(os.path.join(origin_dir, '*.md')):
		_name_ = gen_randome_name()
		detname = os.path.join(out_dir, _name_)
		print(srcname, detname)
		md_processor(srcname).main(detname)
		artfile.write('{}\t{}\n'.format(_name_, os.path.basename(srcname)))
		# shutil.move(srcname, detname)

