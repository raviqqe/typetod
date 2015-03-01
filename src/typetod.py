#!/usr/bin/env python3

import curses
import curses.ascii
import re
import subprocess
import sys
import getopt
import os.path
import time
import collections
import signal
import threading
import getpass
import enum
import urllib.request
import urllib.parse
import http.client


# global parameters

ENDLESS = False
TAB_SPACES = 2
STATUS_BAR = True
RECURSIVE_SEARCH = False
RESULT_SCREEN = True
MENU_SCREEN = True

## min height and width of terminals
MIN_HEIGHT = 8
MIN_WIDTH = 40

## speed unit
U_WPM = 0
U_CPS = 1
SPEED_UNIT = U_WPM

## translation table
TRANS_TABLE = {
  ord(u'\xa0'): ' ',
  ord(u'\xa3'): 'E',
  ord(u'\xe0'): 'a',
  ord(u'\xe1'): 'a',
  ord(u'\xe2'): 'a',
  ord(u'\xe3'): 'a',
  ord(u'\xe4'): 'a',
  ord(u'\xe5'): 'a',
  ord(u'\xe6'): 'ae',
  ord(u'\xe7'): 'c',
  ord(u'\xe8'): 'e',
  ord(u'\xe9'): 'e',
  ord(u'\xea'): 'e',
  ord(u'\xeb'): 'e',
  ord(u'\u2010'): '-',
  ord(u'\u2013'): '-',
  ord(u'\u2018'): "'",
  ord(u'\u2019'): "'",
  ord(u'\u201c'): '"',
  ord(u'\u201d'): '"',
  ord(u'\u2026'): '...',
  ord(u'\u2028'): '\n',
  ord(u'\u2029'): '\n',
  ord(u'\u20ac'): 'C',
  ord(u'\u3000'): ' ',
  ord(u'\u301c'): '~',
  ord(u'\uff01'): '!',
  ord(u'\uff03'): '#',
  ord(u'\uff04'): '$',
  ord(u'\uff05'): '%',
  ord(u'\uff06'): '&',
  ord(u'\uff08'): '(',
  ord(u'\uff09'): ')',
  ord(u'\uff0a'): '*',
  ord(u'\uff0b'): '+',
  ord(u'\uff0c'): ',',
  ord(u'\uff0d'): '-',
  ord(u'\uff0e'): '.',
  ord(u'\uff0f'): '/',
  ord(u'\uff1a'): ':',
  ord(u'\uff1b'): ';',
  ord(u'\uff1c'): '<',
  ord(u'\uff1d'): '=',
  ord(u'\uff1e'): '>',
  ord(u'\uff1f'): '?',
  ord(u'\uff20'): '@',
  ord(u'\uff3b'): '[',
  ord(u'\uff3c'): '\\',
  ord(u'\uff3d'): ']',
  ord(u'\uff3e'): '^',
  ord(u'\uff40'): '`',
  ord(u'\uff5b'): '{',
  ord(u'\uff5c'): '|',
  ord(u'\uff5d'): '}',
  ord(u'\ufffd'): '?',
}


# exceptions

class FailException(Exception):
  def __init__(self, message):
    self.message = message

  def __str__(self):
    return repr(self.message)


# classes

class Game:
  SEPARATE_SAMPLES = True
  KEEP_EMPTY_LINES = True # in sample texts
  SEP_LINE_CHAR = '-'
  A_CORRECT = curses.A_NORMAL
  A_ERROR = curses.A_REVERSE
  MORPHING = False
  ERASE_MULTIPLE_SPACE = False

  def __init__(self, window):
    self.window = window
    self.sample_t = collections.deque([])
    self.input_t = ""
    self.width = self.window.getmaxyx()[1]
    # evaluation variables
    self.start_time = 0
    self.type_num = 0
    self.error_num = 0
    # generate the line layout
    self.input_line = self.window.getmaxyx()[0] // 2
    self.sample_lines = []
    self.sep_lines = []
    self.curr_sample_line = 0
    for y in range(self.window.getmaxyx()[0]):
      if y <= self.input_line - 3:
        self.curr_sample_line += 1
        self.sample_lines.append(y)
      elif y == self.input_line - 2:
        self.sep_lines.append(y)
      elif y == self.input_line - 1:
        self.sample_lines.append(y)
      elif y == self.input_line + 1:
        self.sep_lines.append(y)
      elif y >= self.input_line + 2:
        self.sample_lines.append(y)
    for i in range(self.curr_sample_line + 1):
      self.sample_t.append("")
    self.first_sample = True

  def start(self):
    self.__new_line()
    self.start_time = time.time()

  def save_result(self):
    self.speed = self.get_speed()

  def is_over(self):
    if len(self.sample_t) <= self.curr_sample_line:
      return True
    else:
      return False

  def is_almost_over(self):
    if len(self.sample_t) < len(self.sample_lines) + 4:
      return True
    else:
      return False

  def add_sample(self, text):
    if self.SEPARATE_SAMPLES and self.KEEP_EMPTY_LINES \
        and not self.first_sample:
      self.sample_t += [""]
    elif self.first_sample:
      self.first_sample = False
    self.sample_t += self.__format(uni_to_ascii(text))

  def add_char(self, char):
    self.type_num += 1
    if (char == ' ' or char == '\n') \
        and self.input_t == self.sample_t[self.curr_sample_line]:
      self.__new_line()
    elif char == '\n' or len(self.input_t) == self.width \
        or len(self.input_t) == len(self.sample_t[self.curr_sample_line]):
      self.error_num += 1
    elif char == '\t':
      correct = True
      for i in range(TAB_SPACES):
        if not self.__add_char(' ') and correct:
          self.error_num += 1
          correct = False
        if len(self.input_t) == len(self.sample_t[self.curr_sample_line]):
          break
    elif not self.__add_char(char):
      self.error_num += 1
    if self.MORPHING:
      self.__morph()
    if self.is_over():
      self.save_result()

  def __add_char(self, char):
    self.input_t += char
    if self.input_t[-1] \
        == self.sample_t[self.curr_sample_line][len(self.input_t) - 1]:
      self.window.addstr(char, self.A_CORRECT)
      return True
    else:
      self.window.addstr(char, self.A_ERROR)
      return False

  def del_char(self):
    if len(self.input_t) != 0:
      self.input_t = self.input_t[:-1]
      self.window.move(self.input_line, len(self.input_t))
      self.window.clrtoeol()
    if self.MORPHING:
      self.__morph()

  def clear_input_line(self):
    if self.MORPHING:
      self.window.addstr(self.input_line - 1, 0,
          self.sample_t[self.curr_sample_line])
    self.input_t = '' 
    self.window.move(self.input_line, 0)
    self.window.clrtoeol()

  def __morph(self):
    if (len(self.input_t) > self.width // 2 or len(self.input_t) > 40) \
        and len(self.sample_t) > self.curr_sample_line + 1:
      y, x = self.window.getyx()
      self.window.addstr(self.input_line - 1, 0,
          self.sample_t[self.curr_sample_line])
      self.window.addstr(self.input_line - 1, 0,
          self.sample_t[self.curr_sample_line + 1][:len(self.input_t)
          - min(self.width // 2, 40)])
      if len(self.sample_t[self.curr_sample_line + 1]) \
          < len(self.input_t) - min(self.width // 2, 40):
        self.window.addstr(' ' * (len(self.input_t)
            - min(self.width // 2, 40)
            - len(self.sample_t[self.curr_sample_line + 1])))
      self.window.addch(' ', curses.A_REVERSE)
      self.window.move(y, x)
    elif (len(self.input_t) == self.width // 2 or len(self.input_t) == 40) \
        and len(self.sample_t) > self.curr_sample_line + 1:
      y, x = self.window.getyx()
      self.window.addstr(self.input_line - 1, 0,
          self.sample_t[self.curr_sample_line])
      self.window.move(y, x)

  def get_speed(self):
    try:
      return self.speed # when the game is over
    except:
      if SPEED_UNIT == U_WPM:
        return '{:>5.1f}wpm'.format((self.type_num - self.error_num)
            / (time.time() - self.start_time) / 5 * 60)
      elif SPEED_UNIT == U_CPS:
        return '{:>5.2f}cps'.format((self.type_num - self.error_num)
            / (time.time() - self.start_time))
      else:
        raise FailException('invalid SPEED_UNIT')

  def get_accuracy(self):
    if self.type_num == 0:
      return '  0%'
    else:
      return '{:>3.0f}%'.format((self.type_num - self.error_num)
          / self.type_num * 100)

  def get_errors(self):
    return '{:>3d}'.format(self.error_num)

  def typed(self):
    return self.type_num > 0

  def __new_line(self):
    self.input_t = ""
    self.sample_t.popleft()
    self.window.erase()
    # display sample texts
    if len(self.sample_t) < len(self.sample_lines):
      for i, text in enumerate(self.sample_t):
        self.window.addstr(self.sample_lines[i], 0, text)
    else:
      for i, y in enumerate(self.sample_lines):
        self.window.addstr(y, 0, self.sample_t[i])
    # display separation lines
    for y in self.sep_lines:
      self.window.addstr(y, 0, self.SEP_LINE_CHAR * self.width)
    self.window.move(self.input_line, 0)
 
  def __format(self, text):
    t = []
    text = re.sub(r'^\n+', '', re.sub(r' +\n', r'\n',
        re.sub(r'[ \n]+$', '', conv_tabs(text))))
    if not self.KEEP_EMPTY_LINES:
      text = re.sub(r'\n+', r'\n', text)
    if self.ERASE_MULTIPLE_SPACE:
      text = re.sub(r'\n +', r'\n', re.sub(' +', ' ', text))
    while len(text) > 0:
      index = text.find('\n', 0, self.width)
      if index >= 0:
        t.append(text[:index])
        text = text[index + 1:]
      # leave one space at the end of the line on terminals
      # when it ends normally without too long a word.
      elif len(text) < self.width:
        t.append(text)
        break
      else:
        index = text.rfind(' ', 0, self.width)
        if index >= 0:
          t.append(text[:index])
          text = text[index + 1:]
        else:
          t.append(text[:self.width])
          text = text[self.width:]
    return t if not (t == [] and self.KEEP_EMPTY_LINES) else ['']

class Boss(threading.Thread):
  def __init__(self, game):
    threading.Thread.__init__(self)
    self.game = game

  def run(self):
    while True:
      self.assign_tasks()
      time.sleep(4)
      # 80[char] / (200[wpm] * 5[char/word] / 60[s/m]) = 4.8[s]

  def assign_tasks(self):
    while self.game.is_almost_over() and items.is_left():
      self.game.add_sample(items.popleft().get_content())

class Screen(enum.Enum):
  hello = 0
  menu = 1
  game = 2
  result = 3
  leave = 4
  exit = 5

  @classmethod
  def go_to_next_game(cls):
    if MENU_SCREEN and not ENDLESS:
      return cls.menu
    else:
      return cls.game

  @classmethod
  def again_or_not(cls, window):
    while True:
      char = window.getch()
      if char == curses.ascii.ESC or char == 5 \
          or char == ord('n') or char == ord('N'): # 5 is ctrl + 'e'
        window.addstr('n')
        return Screen.exit
      elif char == ord('y') or char == ord('Y') or char == curses.ascii.NL:
        window.addstr('y')
        return cls.go_to_next_game()

class Items(collections.deque):
  def set_next(self, index):
    self.appendleft(self[index])
    del self[index + 1]

  def is_left(self):
    return bool(len(self))

class Fortunes(Items):
  def set_next(self, index):
    self.appendleft(self[index])
    self[index + 1] = fortune()

class Stdin(Items):
  def __init__(self, fo):
    self.stdin = fo
    self.buffer = self.stdin.readline()

  def popleft(self):
    tmp = self.buffer
    self.buffer = self.stdin.readline()
    return Item(tmp, tmp)

  def is_left(self):
    return bool(self.buffer)

class Item:
  def __init__(self, title, content):
    self.title = title
    self.content = content

  def get_title(self):
    return self.title

  def get_content(self):
    return self.content

class LocalFile(Item):
  def __init__(self, filename):
    self.title = filename

  def get_content(self):
    with open(self.title, 'r') as fo:
      return fo.read()

class RemoteFile(Item):
  def __init__(self, url):
    self.title = url

  def get_content(self):
    with urllib.request.urlopen(self.title) as res:
      return res.read().decode('utf-8', 'replace')


# functions

def perror(err_msg):
  print("ERROR:", err_msg, file=sys.stderr)

def fail(err_msg):
  perror(err_msg)
  exit(1)

def conv_tabs(text):
  return text.replace('\t', ' ' * TAB_SPACES)

def fortune():
  text = subprocess.check_output('fortune').decode('ascii')
  return Item(conv_tabs(text.split('\n', 1)[0]), text)

def uni_to_ascii(text):
  return text.translate(TRANS_TABLE).encode('ascii',
      errors='backslashreplace').decode('ascii')


# main routine
if not sys.stdout.isatty():
  fail('stdout is not a tty')

## parse command line arguments
try:
  opts, args = getopt.getopt(sys.argv[1:], 'a:cdefl:mnqrst:w')
except getopt.GetoptError as err:
  fail(str(err))

rss_mode = False
for option, value in opts:
  if option == '-a':
    if value == "reverse":
      Game.A_ERROR = curses.A_REVERSE
    elif value == "blink":
      Game.A_ERROR = curses.A_BLINK
    elif value == "bold":
      Game.A_ERROR = curses.A_BOLD
    elif value == "underline":
      Game.A_ERROR = curses.A_UNDERLINE
    elif value == "normal":
      Game.A_ERROR = curses.A_NORMAL
    else:
      fail("the argument, '{}' of -a option is invalid\n"
          "valid arguments are 'reverse' (default), 'undreline', "
          "'blink', 'bold', and 'normal'".format(value))
  elif option == '-c':
    SPEED_UNIT = U_CPS
  elif option == '-d':
    ENDLESS = True
  elif option == '-e':
    Game.KEEP_EMPTY_LINES = False
  elif option == '-f':
    rss_mode = True
  elif option == '-l':
    if len(value) != 1:
      fail('the argument of -l option must be one character')
    Game.SEP_LINE_CHAR = value
  elif option == '-m':
    MENU_SCREEN = not MENU_SCREEN
  elif option == '-n':
    Game.MORPHING = True
  elif option == '-q':
    RESULT_SCREEN = False
    STATUS_BAR = False
  elif option == '-r':
    RECURSIVE_SEARCH = True
  elif option == '-s':
    STATUS_BAR = False
  elif option == '-t':
    if value.isnumeric():
      TAB_SPACES = int(value)
    else:
      fail('the argument of option, -e must be an integer')
  elif option == '-w':
    Game.ERASE_MULTIPLE_SPACE = True

if not os.isatty(0) and len(args) == 0:
  ENDLESS = True
  Game.SEPARATE_SAMPLES = False
  os.dup2(0, 3)
  os.close(0)
  sys.stdin = open('/dev/tty', 'r')
  items = Stdin(os.fdopen(3, 'r'))
elif not os.isatty(0):
  fail('no argument is needed in stdin mode')
elif rss_mode and len(args) == 1:
  import feedparser
  print('downloading the rss feed from the url...')
  feed = feedparser.parse(args[0])
  if feed["bozo"] != 0:
    fail('could not fetch rss feeds. check the url.')
  if len(feed['items']) == 0:
    fail('no item found in the rss feed')
  items = Items([])
  for item in feed["items"]:
    items.append(Item(item['title'], '# ' + item['title'] + '\n'
        + re.sub(r'<[^<>]+>', '',
        re.sub(r'\s*</\s*p\s*>\s*<\s*p([^>]|(".*")|(\'.*\'))*>\s*', '\n\n',
        item['summary']))))
elif rss_mode:
  fail('assign one url as an argument to play in rss mode')
elif len(args) > 0:
  items = Items([])
  for filename in args:
    if os.path.isfile(filename):
      items.append(LocalFile(filename))
    elif os.path.isdir(filename) and RECURSIVE_SEARCH:
      for file_in_dir in os.listdir(filename):
        if os.path.isfile(os.path.join(file_in_dir, f)):
          items.append(LocalFile(file_in_dir))
    else:
      url = urllib.parse.urlparse(filename)
      if url.scheme == 'http' or url.scheme == 'https':
        if url.scheme == 'http':
          conn = http.client.HTTPConnection(url.netloc)
        elif url.scheme == 'https':
          conn = http.client.HTTPSConnection(url.netloc)
        conn.request('HEAD', url.path)
        status = conn.getresponse().status
        conn.close()
        if status < 400:
          items.append(RemoteFile(filename))
        else:
          fail("url, {} is invalid".format(filename))
      else:
        fail("resource, '{}' doesn't exist or invalid".format(filename))
else:
  MENU_SCREEN = not MENU_SCREEN
  items = Fortunes([])
  for i in range(24):
    items.append(fortune())

err_msg = ''
try:
  # CAUTION
  # use raise statement and FailException() to print error message instead of
  # fail().
  # fail() can result in unpreferred state of terminals.

  # initialization
  window = curses.initscr()
  curses.noecho()
  curses.cbreak()
  curses.start_color()
  curses.use_default_colors()
  window.keypad(True)

  if window.getmaxyx()[0] < MIN_HEIGHT or window.getmaxyx()[1] < MIN_WIDTH:
    raise FailException('your\nterminal\nis\ntoo\nsmall.\nbuy\nanother\n'
        'bigger\none.')
 
  screen = Screen.hello
  while True:
    if screen == Screen.hello:
      window.clear()
      window.addstr(0, 0, "hello, {}! are you ready?"
          .format(getpass.getuser()))
      window.addstr(1, 0, "press any key...")
      char = window.getch()
      if char == curses.ascii.ESC or char == 5: # 5 is ctrl + 'e'
        screen = Screen.exit
      else:
        if STATUS_BAR:
          notebook = window.derwin(window.getmaxyx()[0] - 1,
              window.getmaxyx()[1], 0, 0)
          bar = window.derwin(1, window.getmaxyx()[1],
              window.getmaxyx()[0] - 1, 0)
        else:
          notebook = window.derwin(window.getmaxyx()[0],
              window.getmaxyx()[1], 0, 0)
        notebook.keypad(True)
        screen = Screen.go_to_next_game()

    elif screen == Screen.menu: # for resources mode
      window.clear()
      window.refresh()
      pad = curses.newpad(len(items), window.getmaxyx()[1])
      pad.keypad(True)
      for i, item in enumerate(items):
        pad.addstr(i, 0, '> ' + item.get_title()
            if len(item.get_title()) + 2 < pad.getmaxyx()[1]
            else '> ' + item.get_title()[:pad.getmaxyx()[1] - 6] + '...')
      pad.move(0, 0)
      pad.refresh(0, 0, 0, 0, window.getmaxyx()[0] - 1,
          window.getmaxyx()[1] - 1)
      pos = 0
      while True:
        char = pad.getch()
        if char == curses.ascii.ESC or char == 5: # 5 is ctrl + 'e'
          screen = Screen.leave
          break
        elif char == curses.ascii.NL or char == ord(' '):
          items.set_next(pos)
          screen = Screen.game
          break
        elif char == ord('j') or char == curses.KEY_DOWN:
          pos = min(pos + 1, pad.getmaxyx()[0] - 1)
        elif char == ord('k') or char == curses.KEY_UP:
          pos = max(pos - 1, 0)
        pad.move(pos, 0)
        # scrolling the pad
        if pad.getmaxyx()[0] - 1 - pos <= (window.getmaxyx()[0] - 1) // 2:
          pad.refresh(pad.getmaxyx()[0] - window.getmaxyx()[0], 0,
              0, 0, window.getmaxyx()[0] - 1, window.getmaxyx()[1] - 1)
        elif pos >= window.getmaxyx()[0] // 2:
          pad.refresh(pos - window.getmaxyx()[0] // 2, 0, 0, 0,
              window.getmaxyx()[0] - 1, window.getmaxyx()[1] - 1)
        else:
          pad.refresh(0, 0, 0, 0, window.getmaxyx()[0] - 1,
              window.getmaxyx()[1] - 1)
      pad.keypad(False)
  
    elif screen == Screen.game:
      game = Game(notebook)
      game.add_sample(items.popleft().get_content())
      if ENDLESS:
        boss = Boss(game)
        boss.daemon = True
        boss.assign_tasks()
        boss.start()

      if STATUS_BAR:
        def timer_handler(signum, frame):
          bar.addstr(0, 0, 'speed: {}, accur: {}, typos: {} '.format(
              game.get_speed(), game.get_accuracy(), game.get_errors()),
              curses.A_REVERSE)
          bar.refresh()
          notebook.refresh()
        signal.signal(signal.SIGALRM, timer_handler)
        signal.setitimer(signal.ITIMER_REAL, 0.01, 1)
        bar.refresh()

      game.start()
      notebook.refresh()
      while not game.is_over():
        char = notebook.getch()
        if char == curses.ascii.ESC or char == 5: # 5 is ctrl + 'e'
          if ENDLESS and RESULT_SCREEN and game.typed():
            game.save_result()
            screen = Screen.result
          else:
            screen = Screen.leave
          break
        elif char == 21: # 21 is ctrl + 'u'
          game.clear_input_line()
        elif char == curses.KEY_BACKSPACE or char == curses.KEY_DC:
          game.del_char()
        elif 32 <= char <= 126 \
            or char == curses.ascii.NL \
            or char == curses.ascii.TAB: # space to tilda in ascii
          game.add_char(chr(char))
        notebook.refresh()
      else:
        if RESULT_SCREEN:
          screen = Screen.result
        else:
          screen = Screen.leave
      if STATUS_BAR:
        signal.setitimer(signal.ITIMER_REAL, 0)

    elif screen == Screen.result:
      window.clear()
      if ENDLESS:
        window.addstr(0, 0, "you survived!")
      else:
        window.addstr(0, 0, "you did it!")
      window.addstr(1, 0, "{:9s} {:>8s}"
          .format('speed:', game.get_speed()))
      window.addstr(2, 0, "{:9s} {:>6s}"
          .format('accuracy:', game.get_accuracy()))
      window.addstr(3, 0, "{:9s} {:>5s}"
          .format('typos:', game.get_errors()))
      window.addstr(4, 0, "press any key...")
      window.getch()
      screen = Screen.leave
  
    elif screen == Screen.leave:
      window.clear()
      window.addstr(0, 0, "leaving a game...")
      if not items.is_left() or ENDLESS:
        window.addstr(1, 0, "press any key...")
        window.getch()
        screen = Screen.exit
      else:
        window.addstr(1, 0, "again? (y/n): ")
        screen = Screen.again_or_not(window)
        window.refresh()

    elif screen == Screen.exit:
        break
        
  # finalization
  if 'notebook' in locals():
    notebook.keypad(False)
except FailException as e:
  err_msg = e.args[0]
except KeyboardInterrupt:
  err_msg = 'stopped'
finally:
  if 'window' in locals():
    window.keypad(False)
    curses.nocbreak()
    curses.echo()
    curses.endwin() # this should be in the very last line

if err_msg:
  perror(err_msg)
