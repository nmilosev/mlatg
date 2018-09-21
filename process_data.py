#!/usr/bin/python3
import csv
import glob
from tqdm import tqdm
import numpy
from collections import OrderedDict
import spacy

def ascii(s, nlp, lower=True):
    replacemap = [('š', 's'), ('đ', 'dj'), ('č', 'c'), ('ć', 'c'), ('ž', 'z')]
    if lower:
        s = s.lower()
    for a, b in replacemap:
        s = s.replace(a, b)
    s = s.replace('\n', '')
    s = s.strip()
    try:
        s = " ".join([token.text for token in nlp(s)])
    except :
        pass
    return s


if __name__ == '__main__':

    files = glob.glob('data-raw/*.csv')
    files = [f for f in files if 'responses' in f]

    nlp = spacy.load('../fasttext/spacy-fasttext-sr')

    qdict = OrderedDict()
    qcount = 1

    print('Reading files...')

    for fi, filename in tqdm(enumerate(files), total=len(files)):
        respp = filename
        gradep = filename.replace('responses', 'grades')

        with open(respp, newline='') as rf, open(gradep, newline='') as gf, open('out.csv', 'a', newline='') as outf:
            rreader = csv.reader(rf, delimiter=',', quotechar='"')
            greader = csv.reader(gf, delimiter=',', quotechar='"')
            writer = csv.writer(outf, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            grows = [l[11:] for l in list(greader)]

            for j, row in enumerate(rreader):
                if 'Surname' not in row[0]:
                    data = row[11:]
                    for i in range(0, 10):
                        q, a, _ = data[i*3:i*3+3]
                        g = grows[j][i]
                        g = g if g != '-' else '0.00'
                        if len(a) > 0 and a != '-':
                            #qdict["{}-{}".format(fi, i)] = ascii(q, lower=False)
                            writer.writerow([g, ascii(a, nlp), ascii(q, nlp), respp, i + 1])

    # with open('out.csv', 'a', newline='') as outf:
    #     writer = csv.writer(outf, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    #     for i in qdict.keys():
    #         writer.writerow([qdict[i]])