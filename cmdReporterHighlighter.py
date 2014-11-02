# -*- coding: UTF-8 -*-

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

# How to use it
# open script editor and run
#
# import cmdReporterHighlighter as crHighlighter
# crHighlighter.highlightCmdReporter()

import sys
import os
import re
import keyword

from maya import cmds
from maya import OpenMayaUI as omui

from PySide import QtGui, QtCore


def getMayaWindowWidget():
    '''get maya window widget for Qt'''
    mwin = None
    try:
        from shiboken import wrapInstance
        mwinPtr = omui.MQtUtil.mainWindow()
        mwin = wrapInstance(long(mwinPtr), QtGui.QMainWindow)
    except:
        mapp = QtGui.QApplication.instance()
        for widget in mapp.topLevelWidgets():
            if widget.objectName() == 'MayaWindow':
                mwin = widget
                break
    return mwin

def highlightCmdReporter():
    '''find cmdScrollFieldReporter and highlight it'''
    mwin = getMayaWindowWidget()
    cmdReporters = cmds.lsUI(type='cmdScrollFieldReporter')
    if not cmdReporters: return
    # only setup for the first one
    cmdReporter = mwin.findChild(QtGui.QTextEdit, cmdReporters[0])
    highlighter = Highlighter(parent=mwin)
    highlighter.setDocument(cmdReporter.document())

class Highlighter(QtGui.QSyntaxHighlighter):
    """syntax highlighter"""
    def __init__(self, parent=None):
        super(Highlighter, self).__init__(parent)

        self.__rules = []

        # keywords color
        self._keywordColor = QtGui.QColor(0, 128, 255)

        self._keywordFormat()
        self._cmdsFunctionFormat()

        # maya api format
        mapiFormat = QtGui.QTextCharFormat()
        mapiFormat.setForeground(self._keywordColor)
        self.__rules.append((re.compile('\\bM\\w+\\b'), mapiFormat))
        # Qt
        self.__rules.append((re.compile('\\bQ\\w+\\b'), mapiFormat))

        # quotation
        self._quotationFormat = QtGui.QTextCharFormat()
        self._quotationFormat.setForeground(QtCore.Qt.green)
        # quote: ""
        self.__rules.append((re.compile('".*"'), self._quotationFormat))
        # single quotes for python: ''
        self.__rules.append((re.compile("'.*'"), self._quotationFormat))

        # sing line comment
        self._commentFormat = QtGui.QTextCharFormat()
        # orange red
        self._commentFormat.setForeground(QtGui.QColor(255, 128, 64))
        # // mel comment
        self.__rules.append((re.compile('//[^\n]*'), self._commentFormat))
        # # python comment
        self.__rules.append((re.compile('#[^\n]*'), self._commentFormat))

        # function and class format
        funcFormat = QtGui.QTextCharFormat()
        funcFormat.setFontWeight(QtGui.QFont.Bold)
        self.__rules.append((re.compile('\\b(\\w+)\(.*\):'), funcFormat))

        # mel warning
        warningFormat = QtGui.QTextCharFormat()
        warningFormat.setForeground(QtGui.QColor('#FF9ACD32'))
        warningFormat.setBackground(QtCore.Qt.yellow)
        warningFormat.setFontWeight(QtGui.QFont.Bold)
        self.__rules.append((re.compile('// Warning:[^\n]*//'), warningFormat))

        # mel error
        errorFormat = QtGui.QTextCharFormat()
        errorFormat.setForeground(QtGui.QColor('#FF9ACD32'))
        errorFormat.setBackground(QtCore.Qt.red)
        errorFormat.setFontWeight(QtGui.QFont.Bold)
        self.__rules.append((re.compile('// Error:[^\n]*//'), errorFormat))

        # blocks: start : end
        self._blockRegexp = {
                            '"""\\*' : ('\\*"""', self._quotationFormat),
                            # python  multi-line string: '''   '''
                            "'''\\*" : ("\\*'''", self._quotationFormat),
                            }

        # mel multi-line comment: /*  */
        self._melMLComStart = re.compile('/\\*')
        self._melMLComEnd = re.compile('\\*/')

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
        keywordFormat.setForeground(self._keywordColor)
        keywordFormat.setFontWeight(QtGui.QFont.Bold)
        kwtext = '\\b('
        for kw in keywords:
            kwtext += kw + "|"
        kwtext = kwtext[:-1] + ')\\b'
        self.__rules.append((re.compile(kwtext), keywordFormat))

    def _cmdsFunctionFormat(self):
        '''set up maya.cmds functions'''
        mayaBinDir = os.path.dirname(sys.executable)
        cmdsList = os.path.join(mayaBinDir, 'commandList')
        functions = '\\b('
        with open(cmdsList) as phile:
            for line in phile:
                functions += line.split(' ')[0] + '|'

        # global MEL procedures
        melProcedures = cmds.melInfo()
#        melProcedures_00 = '\\b('
        melProc = []
        melProc.append('\\b(' + '|'.join(melProcedures[:1400]) + ')\\b')
        melProc.append('\\b(' + '|'.join(melProcedures[1400:2800]) + ')\\b')
        melProc.append('\\b(' + '|'.join(melProcedures[2800:4200]) + ')\\b')
        melProc.append('\\b(' + '|'.join(melProcedures[4200:5400]) + ')\\b')
        melProc.append('\\b(' + '|'.join(melProcedures[5400:6600]) + ')\\b')
        melProc.append('\\b(' + '|'.join(melProcedures[6600:7800]) + ')\\b')
        #melProc.append('\\b(' + '|'.join(melProcedures[7800:8000]) + ')\\b')
        melProc.append('\\b(' + '|'.join(melProcedures[7800:]) + ')\\b')

        # TODO: should update it when a plug-in was load.
        # function from plug-ins
        plugins = cmds.pluginInfo(q=1, listPlugins=1)
        for plugin in plugins:
            funcFromPlugin = cmds.pluginInfo(plugin, q=1, command=1)
            if funcFromPlugin:
                functions += '|'.join(funcFromPlugin)
        functions = functions[:-1] + ')\\b'

        # function format
        funcFormat = QtGui.QTextCharFormat()
        funcFormat.setForeground(self._keywordColor)
        self.__rules.append((re.compile(functions), funcFormat))
        for mp in melProc:
            self.__rules.append((re.compile(mp), funcFormat))

    def _melMLCommentFormat(self, text):
        '''set up mel multi-line comment: /*  */'''
        startIndex = 0
        commentLen = 0
        self.setCurrentBlockState(0)
        if self.previousBlockState() != 1:
            searchStart = self._melMLComStart.search(text)
            if searchStart:
                startIndex = searchStart.start()
                searchEnd = self._melMLComEnd.search(text)
                if searchEnd:
                    commentLen = searchEnd.end() - startIndex
                else:
                    self.setCurrentBlockState(1)
                    commentLen = len(text) - startIndex
        else:
            searchEnd = self._melMLComEnd.search(text)
            if searchEnd:
                commentLen = searchEnd.end()
            else:
                self.setCurrentBlockState(1)
                commentLen = len(text)
        if commentLen > 0:
            self.setFormat(startIndex, commentLen, self._commentFormat)

    def highlightBlock(self, text):
        '''highlight text'''
        for regExp, tformat in self.__rules:
            match = regExp.search(text)
            if match:
                self.setFormat(match.start(), match.end() - match.start(), tformat)
#             while match != None:
#                 self.setFormat(match.start(), match.end() - match.start(), tformat)
#                 match = regExp.search(text, match.start())

        # blocks
        self._melMLCommentFormat(text)
        textLength = len(text)
        for startBlock in self._blockRegexp:
            startIndex = 0
            startRegExp = QtCore.QRegExp(startBlock)
            endRegExp = QtCore.QRegExp(self._blockRegexp[startBlock][0])
            if self.previousBlockState() != 1:
                startIndex = startRegExp.indexIn(text)

            while startIndex >= 0:
                endIndex = endRegExp.indexIn(text, startIndex)
                if endIndex == -1:
                    self.setCurrentBlockState(1)
                    blockLength = textLength - startIndex
                else:
                    blockLength = endIndex - startIndex + endRegExp.matchedLength()

                self.setFormat(startIndex, blockLength, self._blockRegexp[startBlock][1])
                startIndex = startRegExp.indexIn(text, startIndex + blockLength)
