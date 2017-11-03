import numpy as np
from util import *

class Object:
	def __init__(self, name='main'):
		self.trans = []
		self.name = name

	def add(self, fold):
		self.trans.append(fold)

	def DE(self, origin):
		p = np.copy(origin)
		d = 1e20
		for t in self.trans:
			if hasattr(t, 'fold'):
				#if hasattr(t, 'o'):
				#	t.o = origin
				t.fold(p)
			elif hasattr(t, 'DE'):
				d = min(d, t.DE(p))
			else:
				raise Exception("Invalid type in transformation queue")
		return d

	def NP(self, origin):
		undo = []
		p = np.copy(origin)
		d = 1e20
		n = np.zeros((3,), dtype=np.float32)
		for t in self.trans:
			undo.append((t, np.copy(p)))
			if hasattr(t, 'fold'):
				#if hasattr(fold, 'o'):
				#	fold.o = origin
				t.fold(p)
			elif hasattr(t, 'NP'):
				pass
			else:
				raise Exception("Invalid type in transformation queue")
		for t, p in undo[::-1]:
			if hasattr(t, 'fold'):
				t.unfold(p, n)
			elif hasattr(t, 'NP'):
				cur_n = t.NP(p)
				cur_d = norm_sq(cur_n - p[:3]) / (p[3] * p[3])
				if cur_d < d:
					d = cur_d
					n = cur_n
		return n

	def glsl(self):
		return 'de_' + self.name + '(p)'

	def glsl_col(self):
		return 'col_' + self.name + '(p)'

	def compiled(self):
		s = 'float de_' + self.name + '(vec4 p) {\n'
		#s += '\tvec4 o = p;\n'
		s += '\tfloat d = 1e20;\n'
		for t in self.trans:
			if hasattr(t, 'fold'):
				s += t.glsl()
			elif hasattr(t, 'DE'):
				s += '\td = min(d, ' + t.glsl() + ');\n'
			else:
				raise Exception("Invalid type in transformation queue")
		s += '\treturn d;\n'
		s += '}\n'
		s += 'vec4 col_' + self.name + '(vec4 p) {\n'
		#s += '\tvec4 o = p;\n'
		#s += '\tvec4 orbit = vec4(1e20);\n'
		s += '\tvec4 col = vec4(1e20);\n'
		s += '\tvec4 newCol;\n'
		for t in self.trans:
			if hasattr(t, 'fold'):
				s += t.glsl()
			elif hasattr(t, 'DE'):
				s += '\tnewCol = ' + t.glsl_col() + ';\n'
				s += '\tif (newCol.w < col.w) { col = newCol; }\n'
			else:
				raise Exception("Invalid type in transformation queue")
			#if t.__class__.__name__ == 'FoldScaleTranslate':
			#	s += '\torbit.xyz = min(orbit.xyz, abs(p.xyz));\n'
		s += '\treturn col;\n'
		s += '}\n'
		return s
