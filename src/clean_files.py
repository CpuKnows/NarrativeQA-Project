# Author: John Maxwell
# Date: 2018-03-17
# TLDR: Cleans html and extra text before and after content for NarrativeQA 
#       dataset
# =============================================================================

import codecs
from html.parser import HTMLParser
from tqdm import tqdm
import pandas as pd


class ScriptHTMLParser(HTMLParser):
    """Parses HTML of movie script files"""

    def __init__(self, imsdb_format=False):
        super().__init__()
        self.reset()
        self.fed = []
        self.imsdb_format = imsdb_format
        self.nested = 0
        
    def handle_starttag(self, tag, attrs):
        if self.imsdb_format:
            if tag == 'pre':
                self.nested += 1
                return
            elif self.nested:
                self.nested += 1
                return
            else:
                return
        else:
            pass

    def handle_endtag(self, tag):
        if self.imsdb_format and self.nested:
            self.nested -= 1
        else:
            pass

    def handle_data(self, data):
        if self.imsdb_format:
            if self.nested:
                self.fed.append(data)
        else:
            self.fed.append(data)
            
    def get_data(self):
        return ''.join(self.fed)
    

def clean_files(doc_ids, story_url, doc_dir, output_dir):
    """Cleans all data files. Output file names are appended with '-clean'

    :param doc_ids: list of document ids
    :param story_url: list of story urls
    :param doc_dir: directory containing documents, ex:'tmp/'
    :param output_dir: directory to output cleaned documents, ex:'clean/'
    :return: none
    """
    
    for doc_id, url in tqdm(zip(doc_ids, story_url), total=len(doc_ids)):
        # book
        if 'gutenberg.org' in url:
            with codecs.open(doc_dir + doc_id + '.content', 'r',encoding='utf-8', errors='ignore') as f:
                doc_str = f.read()
                
            start_sentences = [
                '*** START OF THIS PROJECT GUTENBERG EBOOK',
                '***START OF THIS PROJECT GUTENBERG EBOOK',
                '***START OF THE PROJECT GUTENBERG EBOOK',
                '*END THE SMALL PRINT! FOR PUBLIC DOMAIN ETEXTS*',
                '*END*THE SMALL PRINT! FOR PUBLIC DOMAIN ETEXTS*'
            ]
            end_sentences = [
                '*** END OF THIS PROJECT GUTENBERG EBOOK',
                '***END OF THIS PROJECT GUTENBERG EBOOK',
                '***END OF THE PROJECT GUTENBERG EBOOK',
                'End of this Project Gutenberg Etext',
                'End of The Project Gutenberg Etext',
                'End of Project Gutenberg\'s Etext',
                'End of Project Gutenberg Etext',
                'END OF PROJECT GUTENBERG ETEXT',
                'End of the Project Gutenberg etext',
                'End of the Project Gutenberg Etext'
            ]

            for start_sent in start_sentences:
                for end_sent in end_sentences:
                    start_pos = doc_str.find(start_sent)
                    end_pos = doc_str.rfind(end_sent)

                    if start_pos != -1 and end_pos != -1:
                        # Some labels appear twice. We want the the inner most start/end
                        temp_start_pos = doc_str.find(start_sent)
                        temp_end_pos = doc_str.rfind(end_sent)

                        if temp_start_pos != -1 and temp_end_pos != -1:
                            start_pos = temp_start_pos
                            end_pos = temp_end_pos

                        if start_sent[0:4] == '*END':
                            # Offset start to next line if fixed length
                            start_pos += 64
                        break

                if start_pos != -1 and end_pos != -1:
                    break

            if start_pos == -1 or end_pos == -1:
                print('Error: Couldn\'t find start or end position in gutenberg doc: ' + doc_id)
            else:
                doc_str = doc_str[start_pos:end_pos-1]
                
                with codecs.open(output_dir + doc_id + '-clean.content', 'w',encoding='utf-8', errors='ignore') as f:
                    f.write(doc_str)
        
        # movie script
        else:
            with codecs.open(doc_dir + doc_id + '.content', 'r',encoding='utf-8', errors='ignore') as f:
                if ('awesomefilm.com' in url) or ('dailyscript.com' in url):
                    parser = ScriptHTMLParser(imsdb_format=False)
                elif 'imsdb.com' in url:
                    parser = ScriptHTMLParser(imsdb_format=True)
                parser.feed(f.read())
                doc_str = parser.get_data()

            with codecs.open(output_dir + doc_id + '-clean.content', 'w',encoding='utf-8', errors='ignore') as f:
                f.write(doc_str)


if __name__ == '__main__':

    docs = pd.read_csv('../data/documents.csv')
    clean_files(
        docs['document_id'].tolist(), 
        docs['story_url'].tolist(),
        '../data/tmp/', 
        '../data/clean/')
