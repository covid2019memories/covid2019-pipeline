# -*- coding: utf-8 -*-

import re
import codecs


re_src = re.compile('^###.+$')
re_itm = re.compile('^\|\d\d-\d\d\|[^|]+\|\[link\]\(https://mp.weixin.qq.com/[^|]+\|[^|]+\|[^|]+\|[^|]+\|$')

itm = None
src = None

items = []
with open('data/nCovMemory.md') as f:
    for line in f:
        line = line.strip()

        if re_src.match(line):
            src = line[3:].strip()

        if src:
            line = line.replace('\\|', '-')
            if re_itm.match(line):
                fields = line.split('|')
                _, date, title, link, snapshot, archive, _ , _ = fields
                if date > '10-':
                    date = '2019-%s' % date
                else:
                    date = '2020-%s' % date
                title = title.replace('🔥', '').strip()
                link = link[7:-1]
                snapshot = snapshot[7:-1]
                archive = archive[7:-1]

                print(date, src, title, link, snapshot, archive)
                items.append((date, src, title, link, snapshot, archive))


with codecs.open('data/chronological.csv', encoding='utf-8', mode='w') as f:
    for itm in sorted(items):
        date, src, title, link, snapshot, archive = itm
        f.write('%s, %s, "%s", %s, %s, %s\n' % (date, src, title, link, snapshot, archive))