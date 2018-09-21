import re
import random
from torchtext import data
import numpy

class TestsDS(data.Dataset):

    @staticmethod
    def sort_key(ex):
        return len(ex.text)

    def __init__(self, text_field, label_field, examples=None, **kwargs):
        """Create an dataset instance.

        Arguments:
            text_field: The field that will be used for text data.
            label_field: The field that will be used for label data.
            examples: The examples contain all the data.
            Remaining keyword arguments: Passed to the constructor of
                data.Dataset.
        """

        def clean_str(string):
            """
            Tokenization/string cleaning for all datasets except for SST.
            Original taken from https://github.com/yoonkim/CNN_sentence/blob/master/process_data.py
            """
            string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
            string = re.sub(r"\'s", " \'s", string)
            string = re.sub(r"\'ve", " \'ve", string)
            string = re.sub(r"n\'t", " n\'t", string)
            string = re.sub(r"\'re", " \'re", string)
            string = re.sub(r"\'d", " \'d", string)
            string = re.sub(r"\'ll", " \'ll", string)
            string = re.sub(r",", " , ", string)
            string = re.sub(r"!", " ! ", string)
            string = re.sub(r"\(", " \( ", string)
            string = re.sub(r"\)", " \) ", string)
            string = re.sub(r"\?", " \? ", string)
            string = re.sub(r"\s{2,}", " ", string)
            return string.strip()

        text_field.preprocessing = data.Pipeline(clean_str)
        fields = [('text', text_field), ('label', label_field)]

        if examples is None:
            examples = []
            with open('data/testovi.csv', errors='ignore') as f:
                import csv
                reader = csv.reader(f, delimiter=',', quotechar='"')
                # CSV: grade, answer, question, filename, questionnumber
                examples += [
                    data.Example.fromlist([line[2] + ' <pad> ' + line[1], str(round(float(line[0]) * 2) / 2)], fields) for line in reader]

                # under sampling:
                # classes = sorted(set(map(lambda e: e.label, examples)))
                # examples_split = [[e for e in examples if e.label == x] for x in classes]
                # min_class_count = min([len(e) for e in examples_split])
                # examples = []
                #
                # for egroup in examples_split:
                #     random.shuffle(egroup)
                #     examples.extend(egroup[:min_class_count])
                #
                # import numpy as np
                # print(np.unique([e.label for e in examples], return_counts=True))

        super(TestsDS, self).__init__(examples, fields, **kwargs)

    @classmethod
    def splits(cls, text_field, label_field, dev_ratio=.3, shuffle=True, root='.', **kwargs):
        """Create dataset objects for splits of the MR dataset.

        Arguments:
            text_field: The field that will be used for the sentence.
            label_field: The field that will be used for label data.
            dev_ratio: The ratio that will be used to get split validation dataset.
            shuffle: Whether to shuffle the data before split.
            root: The root directory that the dataset's zip archive will be
                expanded into; therefore the directory in whose trees
                subdirectory the data files will be stored.
            train: The filename of the train data. Default: 'train.txt'.
            Remaining keyword arguments: Passed to the splits method of
                Dataset.
        """
        examples = cls(text_field, label_field, **kwargs).examples
        if shuffle: random.shuffle(examples)
        dev_index = -1 * int(dev_ratio*len(examples))

        return (cls(text_field, label_field, examples=examples[:dev_index]),
                cls(text_field, label_field, examples=examples[dev_index:]))

    @classmethod
    def kfold(cls, text_field, label_field, folds=10, shuffle=True, root='.', **kwargs):

        examples = cls(text_field, label_field, **kwargs).examples
        if shuffle: random.shuffle(examples)

        folds = numpy.array_split(examples, folds)

        ret_list = []  # list of train - validate tuples

        for i in range(len(folds)):
            validation_fold = folds[i]
            # everything but the i-th element
            train_folds_lists = [x for index, x in enumerate(folds) if index != i]
            train_folds = []
            for e in train_folds_lists:
                train_folds.extend(e)

            ret_list.append((cls(text_field, label_field, examples=train_folds),
                            cls(text_field, label_field, examples=validation_fold)))

        return ret_list

