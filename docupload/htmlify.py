'''
HTMLify: Convert any fileformat supported by pandoc to HTML5
'''
import glob
import os

import pypandoc
from bs4 import BeautifulSoup


def get_html(doc_file, format = None):
    '''Uses pypandoc to convert uploaded file to HTML5'''

    tmp_loc = '/tmp/uploaded_' + str(doc_file)

    with open(tmp_loc, 'wb') as tmp_file:
        for chunk in doc_file.chunks():
            tmp_file.write(chunk)
    html = pypandoc.convert(
        tmp_loc,
        'html5',
        extra_args=['--extract-media=/tmp'],
        format=format,
        )

    return html

def shift_media(html, doc_name, media_dir):
    soup = BeautifulSoup(html, 'lxml')
    for img in soup.findAll('img'):
        img_src = img['src']
        if img_src[:4] != 'http' and img_src[:2] != '//':
            img_src = img_src.replace(media_dir, '/media/docs/' + doc_name)
        img['src'] = img_src

    os.mkdir('media/docs/' + doc_name)
    for image_original in glob.glob(media_dir + '/image*'):
        image_final = 'media/docs/' + doc_name + '/' + image_original.split('/')[-1]
        os.rename(image_original, image_final)

    html = str(soup)
    return html


class HTMLifier():
    '''
    HTMLifier: Class which handles conversion of any docx/md/tex file to HTML
    '''


    def __init__(self, doc_base_path='.'):
        self.doc_base_path = doc_base_path

    def convert(self, doc_file, editor_ext='docx'):
        '''Middleware function to interface with different <format>_convert functions'''

        file_name = str(doc_file)
        ext = file_name.split('.')[-1]
        file_name = file_name[:len(file_name) - len(ext) - 1]
        doc_dir = self.doc_base_path
        if ext == 'Raw content':
            file_name = doc_file.name
            html = get_html(doc_file, 'md')
            html = shift_media(html, file_name, '/tmp/media')
            ext = editor_ext
        elif ext != 'pdf':
            html = get_html(doc_file)
            html = shift_media(html, file_name, '/tmp/media')

        with open(doc_dir + file_name + '.' + ext, 'wb') as doc_stored:
            for chunk in doc_file.chunks():
                doc_stored.write(chunk)

        if ext == 'pdf':
            with open(doc_dir + file_name + '.pdf', 'wb') as doc_stored:
                for chunk in doc_file.chunks():
                    doc_stored.write(chunk)

            return file_name + '.pdf', ext
        
        with open(doc_dir + file_name + '.html', 'wb') as doc_stored:
            doc_stored.write(bytes(html, 'utf-8'))

        return file_name + '.html', ext
