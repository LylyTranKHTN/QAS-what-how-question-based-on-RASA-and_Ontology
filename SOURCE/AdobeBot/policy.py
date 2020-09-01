import logging

from rasa_core.policies.keras_policy import KerasPolicy

logger = logging.getLogger(__name__)


class AdobePolicy(KerasPolicy):
    def model_architecture(self, input_shape, output_shape):
        """Build a Keras model and return a compiled model."""
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import \
            Masking, LSTM, Dense, TimeDistributed, Activation

        # Build Model
        model = Sequential()

        if len(output_shape) == 1:
            model.add(Masking(mask_value=-1, input_shape=input_shape))
            model.add(LSTM(self.rnn_size))
            model.add(Dense(input_dim=self.rnn_size, units=output_shape[-1]))
        elif len(output_shape) == 2:
            model.add(Masking(mask_value=-1,
                              input_shape=(None, input_shape[1])))
            model.add(LSTM(self.rnn_size, return_sequences=True))
            model.add(TimeDistributed(Dense(units=output_shape[-1])))
        else:
            raise ValueError("Cannot construct the model because"
                             "length of output_shape = {} "
                             "should be 1 or 2."
                             "".format(len(output_shape)))

        model.add(Activation('softmax'))

        model.compile(loss='categorical_crossentropy',
                      optimizer='adam',
                      metrics=['accuracy'])

        logger.debug(model.summary())
        return model