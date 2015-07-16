# Inspired by https://github.com/noahcoad/open-url/blob/st3/open_url.py

import sublime, sublime_plugin
import webbrowser, urllib, urllib.parse, re, os, subprocess

SETTINGS_FILE = "open_require.sublime-settings"

class OpenRequireCommand(sublime_plugin.TextCommand):
  debug = True
  
  def run(self, edit=None, url=None):
    # sublime text has its own open_url command used for things like Help menu > Documentation
    # so if a url is specified, then open it instead of getting text from the edit window
    if url is None:
      url = self.selection()

    # strip quotes if quoted
    if (url.startswith("\"") & url.endswith("\"")) | (url.startswith("\'") & url.endswith("\'")):
      url = url[1:-1]

    cmd = self.get_node_path() + ' -p -e "require.resolve(\'' + url + '\')"; exit 0'
    cwd = os.path.dirname(self.view.file_name())
    absolute_path = subprocess.check_output(cmd, shell=True, cwd=cwd).decode('utf-8').strip()

    # debug info
    if self.debug:
      print("absolute_path: ", absolute_path)

    if os.path.exists(absolute_path):
      self.view.window().open_file(absolute_path)
      return

    if "://" in url:
      webbrowser.open_new_tab(url)
    elif re.search(r"\w[^\s]*\.(?:com|co|uk|gov|edu|tv|net|org|tel|me|us|mobi|es|io)[^\s]*\Z", url):
      if not "://" in url:
        url = "http://" + url
      webbrowser.open_new_tab(url)
    else:
      url = "http://google.com/#q=" + urllib.parse.quote(url, '')
      webbrowser.open_new_tab(url)

  def get_node_path(self):
    platform = sublime.platform()
    node_path = sublime.load_settings(SETTINGS_FILE).get('node_path').get(platform)
    return node_path
 
  def selection(self):
    s = self.view.sel()[0]

    # expand selection to possible URL
    start = s.a
    end = s.b

    # if nothing is selected, expand selection to nearest terminators
    if (start == end): 
      view_size = self.view.size()
      terminator = list('\t\"\'><, []()')

      # move the selection back to the start of the url
      while (start > 0
          and not self.view.substr(start - 1) in terminator
          and self.view.classify(start) & sublime.CLASS_LINE_START == 0):
        start -= 1

      # move end of selection forward to the end of the url
      while (end < view_size
          and not self.view.substr(end) in terminator
          and self.view.classify(end) & sublime.CLASS_LINE_END == 0):
        end += 1

    # grab the URL
    return self.view.substr(sublime.Region(start, end)).strip()