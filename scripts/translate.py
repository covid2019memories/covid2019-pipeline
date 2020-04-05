# -*- coding: utf-8 -*-

import requests
import json
import codecs
import os
import os.path as path
import re
import glob
import time
import sys
import spacy

from pathlib import Path
from hanziconv import HanziConv
from pypinyin import slug


SOURCE = '../covid2019-sources'
TARGET = '../covid2019-memories'


nlp = spacy.load('en')


def tranlate(source, direction, field=''):
    source = source.strip()

    if direction == 'zh2zh-chs':
        return source
    elif direction == 'zh2zh-cht':
        return HanziConv.toTraditional(source)

    time.sleep(0.1)
    print('.', end='')
    sys.stdout.flush()
    payload = {
        "source": source,
        "trans_type": direction,
        "request_id": "demo",
        "detect": True,
    }

    token = os.getenv('TRANSLATOR_TOKEN')
    url = "http://api.interpreter.caiyunai.com/v1/translator"
    headers = {
        'content-type': "application/json",
        'x-authorization': "token %s" % token,
    }

    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

    translation = json.loads(response.text)['target']

    if field == 'source' and d == 'zh2en':
        prob = 0.0
        doc = nlp(translation)
        for token in doc:
            prob += token.prob
        if prob > -50:
            return translation
        else:
            translation = slug(source)

    return translation


for f in sorted(glob.glob('%s/memories/cn/*/*.o.zh-chs.md' % SOURCE)):
    ppth, bname = path.split(f)
    tpth = '%s/%s' % (TARGET, ppth[len(SOURCE):])
    Path(tpth).mkdir(parents=True, exist_ok=True)

    if ppth > 'memories/cn/2020-01-27/':
        for d in ['zh2en', 'zh2ja', 'zh2zh-cht', 'zh2zh-chs']:
            names = bname.split('.')
            names[-2] = d[3:]
            if names[-2][:2] == 'zh':
                names[-3] = 'o'
            else:
                names[-3] = 't'

            fname = '.'.join(names)
            fpth = path.join(tpth, fname)

            print('')
            print(f)
            sys.stdout.flush()
            with codecs.open(fpth, encoding='utf-8', mode='w') as g:

                with codecs.open(f, encoding='utf-8') as orig:
                    output = ''
                    flag = False
                    for ln in orig:
                        if ln[:-1] == '-------------':
                            flag = True
                            output = ln[:-1]
                        else:
                            if flag:
                                segments = ln[:-1].split(':')
                                if segments[0] == 'title' or segments[0] == 'lead' or segments[0] == 'source':
                                    output = '%s: %s' % (segments[0], ''.join(tranlate(''.join(segments[1:]), d, field=segments[0])))
                                else:
                                    output = ln[:-1]
                            else:
                                if ln[:-1] == '':
                                    output = ''
                                else:
                                    if ln[0] == '*' and ln[1] == ' ':
                                        output = '* %s' % ''.join(tranlate(ln[3:-1], d))
                                    elif len(re.findall("^\d+\. ", ln)) > 0:
                                        segment = re.findall("^\d+\. ", ln)[0]
                                        output = segment + ''.join(tranlate(ln[len(segment):-1], d))
                                    elif len(re.findall("^#+", ln)) > 0:
                                        segment = re.findall("^#+", ln)[0]
                                        output = segment + ''.join(tranlate(ln[len(segment):-1], d))
                                    elif ln[:6] == '![img]':
                                        output = ln[:-1]
                                    else:
                                        output = ''.join(tranlate(ln[:-1], d))

                        if d == 'zh2zh-chs' or d == 'zh2zh-cht':
                            if flag:
                                g.write('%s\n' % output)
                        else:
                            g.write('%s\n' % output)
