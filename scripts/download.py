# -*- coding: utf-8 -*-

import codecs
import requests as r
import webpreview as wp
import base64
import hashlib
import os.path as path
import time
import re

from pathlib import Path
from pyquery import PyQuery as pq
from wand.image import Image


SOURCE = ''
TARGET = '../covid2019-sources'



def handle_img(url, cover=True):
    time.sleep(0.3)
    dataurl = None
    if url:
        rv = r.get(url)
        if rv.status_code == 200:
            ctype = rv.headers['content-type'].split('/')[1]
            blob = rv.content
            try:
                with Image(blob=blob, format=ctype) as img:
                    height = 480 * img.height // img.width
                    img.resize(width=480, height=height)

                    with img.convert('jpeg') as converted:
                        blob = converted.make_blob()

                encoded = base64.b64encode(blob).decode()
                dataurl = 'data:image/{};base64,{}'.format('jpeg', encoded)
            except Exception:
                dataurl = None

    if cover:
        if dataurl:
            return dataurl
        else:
            return '-'
    else:
        if dataurl:
            return '\n![img](%s)\n' % dataurl
        else:
            return ''


def download(url):
    rv = r.get(url)
    if rv.status_code == 200:
        html = rv.text

        title, description, image = wp.web_preview(url=url, content=html)
        dataurl = handle_img(image, True)

        text = ""
        dedup = {}
        for elem in pq(html)('section, p, h1, h2, h3, h4, ul, ol, div img'):
            tag = elem.tag
            elem = pq(elem)
            if tag == 'h1':
                segment = '#%s\n\n' % elem.text().strip()
                if segment not in dedup:
                    dedup[segment] = True
                    text += segment
            if tag == 'h2':
                segment = '##%s\n\n' % elem.text().strip()
                if segment not in dedup:
                    dedup[segment] = True
                    text += segment
            if tag == 'h3':
                segment = '###%s\n\n' % elem.text().strip()
                if segment not in dedup:
                    dedup[segment] = True
                    text += segment
            if tag == 'h4':
                segment = '####%s\n\n' % elem.text().strip()
                if segment not in dedup:
                    dedup[segment] = True
                    text += segment
            if tag == 'section' or tag == 'p':
                segment = '%s\n\n' % elem.text().strip().replace('#', '')
                if segment not in dedup:
                    dedup[segment] = True
                    text += segment
            if tag == 'ul':
                text += '\n'
                for line in elem.text().split('\n'):
                    if line:
                        text += '* %s\n' % line
                text += '\n\n'
            if tag == 'ol':
                ix = 1
                text += '\n'
                for line in elem.text().split('\n'):
                    if line:
                        text += '%d. %s\n' % (ix, line)
                        ix += 1
                text += '\n\n'
            if tag == 'img':
                ohtml = elem.outer_html()
                links = re.findall("<img(?:\D+=\"\S*\")*\s+data-src=\"(\S+)\"", ohtml)
                widths = re.findall("<img(?:\D+=\"\S*\")*\s+data-w=\"(\d+)\"", ohtml)
                ratios = re.findall("<img(?:\D+=\"\S*\")*\s+data-ratio=\"(\d+.\d+)\"", ohtml)
                if len(links) > 0 and len(widths) > 0 and len(ratios) > 0 and links[0]:
                    width = int(widths[0])
                    ratio = float(ratios[0])
                    if width > 200 and 0.3 < ratio < 3:
                        imgsrc = links[0]
                        print('  * %s' % imgsrc)
                        text += handle_img(imgsrc, False)

        return title, description, dataurl, text


with codecs.open('data/chronological.csv', encoding='utf-8') as f:
    for ln in f:
        time.sleep(6.0)
        ln = ln[:-1].strip()
        date, source, title, link, snapshot, archive = ln.split(', ')

        if '2020-01-20' < date < '2020-03-31':
            print('- %s %s %s %s' % (date, source, title, link))
            title2, lead, cover, text = download(link)

            if lead:
                lead = lead.replace('\n', '')
                lead = lead.replace('\r', '')
                lead = lead.replace('  ', ' ')
                lead = lead.replace('  ', ' ')
                lead = lead.replace('  ', ' ')
            else:
                lead = '_'

            if title2:
                title = title2

            if cover is None:
                cover = '_'

            if text:
                text = text.replace('  ', ' ')
                lead = lead.replace('\r', '')
                text = text.replace('\n\n\n', '\n\n')
                text = text.replace('\n\n\n', '\n\n')
                text = text.replace('\n\n\n', '\n\n')
                text = text.replace('\n\n\n', '\n\n')

                hash = hashlib.md5(title.encode()).hexdigest()
                print(hash)

                pth = '%s/memories/cn/%s/%s.o.zh-chs.md' % (TARGET, date, hash)
                bpth, _ = path.split(pth)
                Path(bpth).mkdir(parents=True, exist_ok=True)
                with codecs.open(pth, encoding='utf-8', mode='w') as g:
                    g.write(text)
                    g.write('\n-------------\n')
                    g.write('title: %s\n' % title)
                    g.write('source: %s\n' % source)
                    g.write('authors: _\n')
                    g.write('editors: _\n')
                    g.write('proofreader: _\n')
                    g.write('photographer: _\n')
                    g.write('translator: _\n')
                    g.write('via: https://github.com/2019ncovmemory/nCovMemory\n')
                    g.write('link: %s\n' % link)
                    g.write('archive: %s\n' % archive)
                    g.write('snapshot: %s\n' % snapshot)
                    g.write('lead: %s\n' % lead)
                    g.write('cover: %s\n' % cover)
