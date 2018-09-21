# import gensim
# from torch import nn, Tensor
#
#
# def emb_layer_gensim():
#     """Create an Embedding layer from the supplied gensim keyed_vectors."""
#     print('Started loading gensim layer...')
#
#     keyed_vectors = gensim.models.FastText.load_fasttext_format('~/wiki.sr.bin').wv
#
#     emb_weights = Tensor(keyed_vectors.syn0)
#     emb = nn.Embedding(*emb_weights.shape)
#     emb.weight = nn.Parameter(emb_weights)
#     emb.weight.requires_grad = False
#
#     print('Loaded gensim layer.')
#
#     return emb, emb_weights
#
# nlp = Language()  # start off with a blank Language class
# with open('/home/nmilosev/wiki.sr.vec', 'rb') as file_:
#     header = file_.readline()
#     nr_row, nr_dim = header.split()
#     nlp.vocab.reset_vectors(width=int(nr_dim))
#     print('Loading fasttext tokenizer')
#     for line in tqdm(file_, total=nr_row):
#         try:
#             line = line.decode('utf8')
#             pieces = line.split()
#             word = pieces[0]
#             vector = numpy.asarray([float(v) for v in pieces[1:]], dtype='f')
#             if len(vector) == nr_dim:
#                 nlp.vocab.set_vector(word, vector)  # add the vectors to the vocab
#         except:
#             pass


