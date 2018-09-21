#! /usr/bin/env python
import os
import datetime
import torch
import torchtext.data as data
import model
import train
import mydatasets
import argparser
from process_data import ascii
from torchtext.vocab import FastText
from torch.utils.data import DataLoader

args = argparser.parser.parse_args()
print('Loading FastText vectors...')
fast_text = FastText(language='sr', cache='../fasttext')


def load(text_field, label_field, **kargs):
    train_data, dev_data = mydatasets.TestsDS.splits(text_field, label_field, dev_ratio=args.validation_split)
    text_field.build_vocab(train_data, dev_data, vectors=fast_text)
    label_field.build_vocab(train_data, dev_data, vectors=fast_text)

    train_iter, dev_iter = data.Iterator.splits(
                            (train_data, dev_data),
                            batch_sizes=(args.batch_size, len(dev_data)),
                            **kargs)
    return train_iter, dev_iter


print('Loading data...')
text_field = data.Field(lower=True)
label_field = data.Field(sequential=False)
train_iter, dev_iter = load(text_field, label_field, device=-1, repeat=False)
args.embed_num = len(text_field.vocab)
args.class_num = len(label_field.vocab) - 1

args.cuda = (not args.no_cuda) and torch.cuda.is_available(); del args.no_cuda
args.kernel_sizes = [int(k) for k in args.kernel_sizes.split(',')]
args.save_dir = os.path.join(args.save_dir, datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

for attr, value in sorted(args.__dict__.items()):
    print('\t{}={}'.format(attr.upper(), value))

cnn = model.CNN_Text(args)
if args.snapshot is not None:
    print('\nLoading model from {}...'.format(args.snapshot))
    if args.cuda:
        cnn.load_state_dict(torch.load(args.snapshot))
    else:
        cnn.load_state_dict(torch.load(args.snapshot, map_location='cpu'))

if args.cuda:
    torch.cuda.set_device(args.device)
    cnn = cnn.cuda()

if args.predict:
    if args.web:
        import webapp
        webapp.serve(train, cnn, text_field, label_field, args.cuda)
    else:
        import csv
        import random
        import spacy
        nlp = spacy.load('../fasttext/spacy-fasttext-sr')
        with open('data/unique-questions.csv', 'r') as outf:
            lines = list(csv.reader(outf, delimiter=',', quotechar='"'))
            while True:
                q = random.choice(lines)[0]
                predict = ascii(q, nlp) + '<pad>' + ascii(input('{} > '.format(q)), nlp)
                label = train.predict(predict, cnn, text_field, label_field, args.cuda)
                print('\n[Text]  {}\n[Label] {}\n'.format(predict, label))
else:
    try:
        if args.kfold > 0:
            folds = mydatasets.TestsDS.kfold(text_field, label_field, folds=args.kfold)
            fold_results = []
            fold = 1
            for train_data, dev_data in folds:
                print(f'Starting fold {fold} (val. fold {fold}, rest train)...')

                train_iter, dev_iter = data.Iterator.splits(
                    (train_data, dev_data),
                    batch_sizes=(args.batch_size, len(dev_data)), repeat=False)

                args.embed_num = len(text_field.vocab)
                args.class_num = len(label_field.vocab) - 1

                cnn = model.CNN_Text(args)
                train.train(train_iter, dev_iter, cnn, args)

                print(f'\nFinal fold {fold} validation:')
                result = train.eval(dev_iter, cnn, args)

                fold_results.append((fold, result))
                fold += 1

            print('Fold results:', fold_results)
        else:
            train.train(train_iter, dev_iter, cnn, args)
    except KeyboardInterrupt:
        print('Exiting from training early')

