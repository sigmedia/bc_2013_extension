""" from https://github.com/keithito/tacotron """
import re
from utils.text import cleaners
from utils.text.symbols import symbols


class DefaultTextProcessing:
  def __init__(self, cleaner_names):

    self._cleaner_names = cleaner_names

    # Mappings from symbol to numeric ID and vice versa:
    self._symbol_to_id = {s: i for i, s in enumerate(symbols)}
    self._id_to_symbol = {i: s for i, s in enumerate(symbols)}

    # Regular expression matching text enclosed in curly braces:
    self._curly_re = re.compile(r'(.*?)\{(.+?)\}(.*)')


  def text_to_sequence(self, text):
    '''Converts a string of text to a sequence of IDs corresponding to the symbols in the text.

      The text can optionally have ARPAbet sequences enclosed in curly braces embedded
      in it. For example, "Turn left on {HH AW1 S S T AH0 N} Street."

      Args:
        text: string to convert to a sequence
        cleaner_names: names of the cleaner functions to run the text through

      Returns:
        List of integers corresponding to the symbols in the text
    '''
    sequence = []

    # Check for curly braces and treat their contents as ARPAbet:
    while len(text):
      m = self._curly_re.match(text)
      if not m:
        sequence += self._symbols_to_sequence(_clean_text(text))
        break
      sequence += self._symbols_to_sequence(_clean_text(m.group(1)))
      sequence += self._arpabet_to_sequence(m.group(2))
      text = m.group(3)

    return sequence


  def sequence_to_text(self, sequence):
    '''Converts a sequence of IDs back to a string'''
    result = ''
    for symbol_id in sequence:
      if symbol_id in self._id_to_symbol:
        s = self._id_to_symbol[symbol_id]
        # Enclose ARPAbet back in curly braces:
        if len(s) > 1 and s[0] == '@':
          s = '{%s}' % s[1:]
        result += s
    return result.replace('}{', ' ')


  def _clean_text(self, text):
    for name in self._cleaner_names:
      cleaner = getattr(cleaners, name)
      if not cleaner:
        raise Exception('Unknown cleaner: %s' % name)
      text = cleaner(text)
    return text


  def _symbols_to_sequence(self, symbols):
    return [self._symbol_to_id[s] for s in symbols if self._should_keep_symbol(s)]


  def _arpabet_to_sequence(self, text):
    return self._symbols_to_sequence(['@' + s for s in text.split()])


  def _should_keep_symbol(self, s):
    return s in self._symbol_to_id and (s != '_') and (s != '~')

class DictTextProcessing(object):
    def __init__(self, dict_file):
        with open(dict_file) as f_in:
            self._symbols = ["_"] + [l.strip() for l in f_in]

        # Mappings from symbol to numeric ID and vice versa:
        self._symbol_to_id = {s: i for i, s in enumerate(self._symbols)}
        self._id_to_symbol = {i: s for i, s in enumerate(self._symbols)}


    def get_nb_symbols(self):
        return len(self._symbols)

    def encode_text(self, text):
        return self.text_to_sequence(text)

    def text_to_sequence(self, text):
        text = text.strip()
        sequence = []

        # Check for curly braces and treat their contents as ARPAbet:
        for symbol in text.split(" "):
            sequence.append(self._symbol_to_id[symbol])
        return sequence

    def sequence_to_text(self, sequence):
        result = []

        # Check for curly braces and treat their contents as ARPAbet:
        for id in text.split(" "):
            sequence.append(self._id_to_symbol[id])

        return " ".join(result)
