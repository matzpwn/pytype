#!/usr/bin/python
# -*- coding: utf-8 -*-
#   This library is free software; you can redistribute it and/or
#   modify it under the terms of the GNU Lesser General Public
#   License as published by the Free Software Foundation; either
#   version 2.1 of the License, or (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public
#   License along with this library; if not, write to the 
#      Free Software Foundation, Inc., 
#      59 Temple Place, Suite 330, 
#      Boston, MA  02111-1307  USA
#
#   2012 by muffat

# WPM CALCUlATOR formula
# char / 5     = words
# words / time = wps
# wps * 60     = wpm

import socket
import re, sys, os
import textwrap
import colorama
import time
import platform
import threading
from threading import Thread
from urllib import FancyURLopener
from random import choice
from colorama import Fore, Back, Style
from time import sleep
if platform.system() == 'Windows':
    import msvcrt
elif platform.system() == 'Linux':
    import termios, fcntl
auto_correct = False
class KThread(threading.Thread):
    """A subclass of threading.Thread, with a kill() method."""
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False
    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run      # Force the Thread to install our trace.
        threading.Thread.start(self)
    def __run(self):
        """Hacked run function, which installs the trace."""
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup
    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None
    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace
    def kill(self):
        self.killed = True

def get_single_press():
    fd = sys.stdin.fileno()
    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)
    oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
    try:
        while 1:
            try:
                c = sys.stdin.read(1)
                return c
                sys.exit(1)
            except IOError: 
                pass
    finally: 
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

class GetColor(object):
    colorama.init()
    def to_color(self, string, color):
        if platform.system() == 'Linux':
            if color == 'blue':
                return '\033[1;34m'+string+'\033[1;m'
            elif color == 'red':
                return '\033[1;31m'+string+'\033[1;m'
            elif color == 'green':
                return '\033[1;32m'+string+'\033[1;m'
            elif color == 'white':
                return '\033[1;37m'+string+'\033[1;m'
            else:
                return "Are you kidding?"
        elif platform.system() == 'Windows':
      	    if color == 'blue':
                return (Fore.BLUE+string+Style.RESET_ALL)
            elif color == 'green':
                return (Fore.GREEN+string+Style.RESET_ALL)
            elif color == 'red':
                return (Fore.RED+string+Style.RESET_ALL)
            else:
                return "Are you kidding?"
class Fixer(object):
    def word_wrap(self,string, width=80, ind1=0, ind2=0, prefix=''):
        """ word wrapping function.
        string: the string to wrap
        width: the column number to wrap at
        prefix: prefix each line with this string (goes before any indentation)
        ind1: number of characters to indent the first line
        ind2: number of characters to indent the rest of the lines
        """
        string = prefix + ind1 * " " + string
        newstring = ""
        while len(string) > width:
            # find position of nearest whitespace char to the left of "width"
            marker = width - 1
            while not string[marker].isspace():
                marker = marker - 1

            # remove line from original string and add it to the new string
            newline = string[0:marker] + "\n"
            newstring = newstring + newline
            string = prefix + ind2 * " " + string[marker + 1:]

        return newstring + string
    def replacer(self,src):
        text    = src
        special = {
          '<b><a href="/name/.*?/">' : '',
          '</a></b>' :'',
          text[-1] : '',
          ' \n' : '',
          '\n' : '',
          '&gt;' : '>',
          '&lt;' : '<',
          '&#x27;' : '\'',
          '&#xB7;' : '-',
          '&#xC6;' : 'ae',
          '&#x22;' : '\"',
          '&#xf1;' : 'n',
          '&nbsp;' : '',
          '&amp;' : '&',
          'nbsp;' : ''
        }
        for (k,v) in special.items():
            text = text.replace(k, v)
        return text

class MyOpener(FancyURLopener):
    version = 'Mozilla/5.0 (X11; Linux i686; rv:2.0b13pre) Gecko/20110322 Firefox/4.0b13pre'

class import_words:
    def __init__(self):
        self.myopener = MyOpener()
        self.url      = 'http://imdb.com'
    def get_quotes(self):
        open_url    = self.myopener.open('http://www.imdb.com/chart/top')
        url         = open_url.read()
        rurl        = re.findall(r'/title/tt.*?/',url)
        tt_movie    = choice(rurl)
        open_movie  = self.myopener.open(self.url+tt_movie+'quotes')
        movie       = open_movie.read()
        self.rtitle = re.findall(r'<title>(.*?)</title>',movie)
        rmovie      = re.findall(r'<a href="/name/.*?:((.|\n)*?)<br />',movie)
        gw1         = choice(rmovie)
        fix         = Fixer().replacer(gw1[0])
        return Fixer().word_wrap(fix.replace('\n',''), 70)
    def info(self):
        return (self.rtitle[0]).split('(')[0]

def timers():
    global maxa,tot
    tot = []
    try:
        text = range(1,60)
        x = 0
        for i in range(0,len(text)):
            maxa = text[x]
            sys.stdout.write("\r%s" % maxa)
            sys.stdout.flush()
            time.sleep(1)
            x = x + 1
        sys.stdout.write("\r  \r\n") # clean up
    except:
        tot.append(maxa)
def timer():
  global schemer
  schemer = 1
  while True:
    try:
      if sentence == True:
      	break
      else:
        time.sleep(1)
        #sys.stdout.write(str(schemer))
        schemer = schemer + 1
    except:
      break
color = GetColor()
def typing_word(word):
  global correct, wrong, timer, A, complete
  complete = False
  A = KThread(target=timer)
  keyboard = list(word)
  x = 0
  timer = 0
  correct = 0
  wrong = 0
  A.start()
  # Starting single press
  while True:
      n = 0
      total_correct = 0
      for i in range(0,len(word)):
        if platform.system() == 'Linux':
        # Get single press in Linux
          letter = get_single_press()
        elif platform.system() == 'Windows':
        # Get single press in Windows
          letter = msvcrt.getch()
        n = n + 1
        # if there is a space
        if word[x] == ' ':
          if letter == ' ':
            correct = correct + 1
            keyboard[x] = color.to_color(' ','green')
            fix = ''.join(keyboard[0:x+1])
          else:
            wrong = wrong + 1
            continue
            keyboard[x] = color.to_color('^','red')
            fix = (''.join(keyboard[0:x+1])).replace(keyboard[0:x+1],'')
        # there is a real letter
        else:
          if letter == word[x]:  
            for i in range(len(keyboard)):
              if letter == keyboard[x]:
                if word.find(letter) == -1:	
                  keyboard[x] = color.to_color(letter,'red')
                else:
                  correct = correct + 1
                  keyboard[x] = color.to_color(letter,'green')
            fix = (''.join(keyboard[0:x+1])).replace('','')
          else:
            wrong = wrong + 1
            continue
            keyboard[x] = color.to_color(word[x],'red')
            if auto_correct == True:
              fix = (''.join(keyboard[0:x+1])).replace(keyboard[0:x+1],'')
        # count the word as complete as word
        if correct == len(word):
          complete = True
          sys.stdout.write("\r%s" % fix)
          return 0
        else:
          x = x + 1
        sys.stdout.write("\r%s" % fix)

def typing_sentence(word):
    global sentence
    sentence = False
    total_correct = []
    total_wrong = []
    sentence = word.split('\n')
    sentence.append('last item')
    x = 0
    print '##################'
    print '# Begin typing > #'
    print '##################\n'
    print words
    for i in sentence:
        try:
            if i == sentence[-1]:
                sentence = True
            else:
                pass
                if i == sentence[-2]:
                    typing_word(sentence[x])
                else:
                    typing_word(sentence[x]+'\n')
                    total_correct.append(correct)
                    total_wrong.append(wrong)
                    x = x + 1
        except typing_wordError:
            pass
    accuracy = (sum(total_correct)*100)/len(words)
    print '\n\nCorrect\t :',sum(total_correct)/5
    print 'Mistaken :',sum(total_wrong)
    #
    words_ = sum(total_correct)/5
    wps_ = words_ * schemer
    wpm_ = wps_ / 60
    gross = float(schemer)/60
    #print gross
    #print int(words_/gross)
    print 'WPM\t : %s WPM'%(int((sum(total_correct)/5)/(float(schemer)/60)))
    print 'Time\t : [%s] Minutes [%s] Seconds'%(schemer/60,schemer-((schemer/60)*60))
    if accuracy >= 50:
        print 'Accuracy : %s %%'%(color.to_color(str(accuracy),'green'))
    else:
        print 'Accuracy : %s %%'%(color.to_color(str(accuracy),'red'))
        #print 'From the movie : '+get_words.info()
def main():
    global words, get_words
    get_words = import_words()
    words = '''Think you're smart, huh? The guy that hired youze,
he'll just do the same to you. Oh, criminals in this town used
to believe in things. Honor. Respect. Look at you! What do you
believe in, huh? WHAT DO YOU BELIEVE IN?'''
    #words = get_words.get_quotes()
    #words = 'fuck\nyou'
    typing_sentence(words)
if __name__ == '__main__':
    main()