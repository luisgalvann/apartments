from common.data.constants import DICTIONARY_PATH, LOREM_PATH
from sqlalchemy import create_engine
import pandas as pd
import random as rd


class LangManager:
    ''' Manage translations and retrieve random text '''

    def __init__(self):
        ''' Get translations table from sqlite '''

        dict_engine = create_engine(DICTIONARY_PATH)
        self.dictionary = pd.read_sql('dictionary', dict_engine)
        self.act_language = None
        
    def change_language(self, language):
        ''' Change active language in application '''

        self.act_language = language
        
    def translate(self, word):
        ''' Translate word to active language '''

        try:
            df = self.dictionary
            return df[df['text']==word][self.act_language].values[0]
        except:
            pass

    @staticmethod
    def lorem_ipsum(num_lines):
        ''' Get random text lines '''
        
        lines = ''
        try:
            with open(LOREM_PATH, "r") as file:
                text = file.readlines()
            for _ in range(num_lines):
                lines += text[rd.randrange(0, 49)]
            return lines[:-2]  # Delete the lines end "\n"
        except:
            pass
