#-*- coding: UTF-8 -*-

# The MIT License (MIT)
# 
# Copyright (c) 2014 Mack Stone
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys
import os
import keyword

from PySide import QtGui, QtCore
from maya import cmds


def getMayaWindowWidget():
	"get maya window widget for Qt"
	mwin = None
	mapp = QtGui.QApplication.instance()
	for widget in mapp.topLevelWidgets():
		if widget.objectName() == 'MayaWindow':
			mwin = widget
			break
	return mwin

class Highlighter(QtGui.QSyntaxHighlighter):
	"""syntax highlighter"""
	def __init__(self, parent=None):
		super(Highlighter, self).__init__(parent)
		
		self.__rules = []
		
		self._keywordFormat()
		self._cmdsFunctionFormat()
		
		# maya api format
		mapiFormat = QtGui.QTextCharFormat()
		mapiFormat.setForeground(QtCore.Qt.darkBlue)
		self.__rules.append((QtCore.QRegExp('\\bM\\w+\\b'), mapiFormat))
		# Qt 
		self.__rules.append((QtCore.QRegExp('\\bQ\\w+\\b'), mapiFormat))
		
		# sing line comment
		self._commentFormat = QtGui.QTextCharFormat()
		# orange red
		self._commentFormat.setForeground(QtGui.QColor('#FFFF4500'))
		# // mel comment
		self.__rules.append((QtCore.QRegExp('//[^\n]*'), self._commentFormat))
		# # python comment
		self.__rules.append((QtCore.QRegExp('#[^\n]*'), self._commentFormat))
		
		# quotation
		self._quotationFormat = QtGui.QTextCharFormat()
		self._quotationFormat.setForeground(QtCore.Qt.green)
		# quote: ""
		self.__rules.append((QtCore.QRegExp('".*"')))
		# single quotes for python: ''
		self.__rules.append((QtCore.QRegExp("'.*'")))
		
		# function and class format
		funcFormat = QtGui.QTextCharFormat()
		funcFormat.setFontWeight(QtGui.QFont.Bold)
		self.__rules.append((QtCore.QRegExp('\\b(\\w+)\(.*\):')))
		
		# blocks: start : end
		self._blockRegexp = {QtCore.QRegExp('/\\*') : QtCore.QRegExp('\\*/'), 
							QtCore.QRegExp('"""\\*') : QtCore.QRegExp('\\*"""'), 
							QtCore.QRegExp("'''\\*") : QtCore.QRegExp("\\*'''")}
		
	def _keywordFormat(self):
		'''set up keyword format'''
		# mel keyword
		melKeywords = ['false', 'float', 'int', 'matrix', 'off', 'on', 'string', 
					'true', 'vector', 'yes', 'alias', 'case', 'catch', 'break', 
					'case', 'continue', 'default', 'do', 'else', 'for', 'if', 'in', 
					'while', 'alias', 'case', 'catch', 'global', 'proc', 'return', 'source', 'switch']
		# python keyword
		pyKeywords = keyword.kwlist + ['False', 'True', 'None']
		
		keywords = {}.fromkeys(melKeywords)
		keywords.update({}.fromkeys(pyKeywords))
		# keyword format
		keywordFormat = QtGui.QTextCharFormat()
		keywordFormat.setForeground(QtCore.Qt.darkBlue)
		keywordFormat.setFontWeight(QtGui.QFont.Bold)
		self.__rules += [(QtCore.QRegExp('\\b%s\\b' % keyword), keywordFormat) for 
						keyword in keywords]
		
	def _cmdsFunctionFormat(self):
		'''set up maya.cmds functions'''
		mayaBinDir = os.path.dirname(sys.executable)
		cmdsList = os.path.join(mayaBinDir, 'commandList')
		functions = []
		with open(cmdsList) as phile:
			[functions.append(line.split(' ')[0]) for line in phile]
			
		# global MEL procedures
		functions += cmds.melInfo()
		
		# function format
		funcFormat = QtGui.QTextCharFormat()
		funcFormat.setForeground(QtCore.Qt.darkBlue)
		self.__rules += [(QtCore.QRegExp('\\b%s\\b' % keyword), funcFormat) for 
						keyword in functions]
		
