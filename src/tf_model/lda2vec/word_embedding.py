import tensorflow as tf


class WordEmbedding(object):

    def __init__(self, embed_size, vocab_size, sample_size, power=1.0,
                 freqs=None, load_embeds=False, pretrained_embeddings=None):
        self.vocab_size = vocab_size
        self.sample_size = sample_size
        self.power = power
        self.freqs = freqs
        if load_embeds:
            self.embedding = tf.constant(pretrained_embeddings, name='embedding', dtype=tf.float32)
        else:
            self.embedding = tf.Variable(tf.random_uniform([vocab_size, embed_size], -1.0, 1.0), name='embedding')

        # Construct nce loss for word embeddings
        self.nce_weights = tf.Variable(tf.truncated_normal([vocab_size, embed_size], stddev=tf.sqrt(1 / embed_size)),
                                       name='nce_weights')
        self.nce_biases = tf.Variable(tf.zeros([vocab_size]), name='nce_biases')

    def __call__(self, embed, train_labels, *args, **kwargs):
        with tf.name_scope('negative_sampling'):
            train_labels = tf.reshape(train_labels, [tf.shape(train_labels)[0], 1])
            sampler = None
            if self.freqs:
                sampler = tf.nn.fixed_unigram_candidate_sampler(train_labels,
                                                                num_true=1,
                                                                num_sampled=self.sample_size,
                                                                unique=True,
                                                                range_max=self.vocab_size,
                                                                distortion=self.power,
                                                                unigrams=self.freqs)

            # compute nce loss for the batch
            loss = tf.reduce_mean(
                tf.nn.nce_loss(weights=self.nce_weights,
                               biases=self.nce_biases,
                               labels=train_labels,
                               inputs=embed,
                               num_sampled=self.sample_size,
                               num_classes=self.vocab_size,
                               num_true=1,
                               sampled_values=sampler)
            )

        return loss
