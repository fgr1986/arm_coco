
# COPYRIGHT ARM!


import tensorflow as tf

from mbnet3_layers import ConvNormAct, Bneck
from utils import get_layer

class SimpleAttention(tf.keras.layers.Layer):
    def __init__(
            self,
            channels: int,
            do_initial_pool: bool,
            allow_res: bool,
            name: str = "ResidualAttention",
    ):
        super().__init__(name=name)

        self.do_initial_pool = do_initial_pool
        self.channels = channels
        self.allow_res = allow_res

        self.conv = ConvNormAct(
            channels,
            kernel_size=3,
            stride=1,
            padding=1,
            norm_layer="bn",
            act_layer="relu",
            use_bias=False,
            name="inputConv",
        )

        # out channels, exp channels, kernel, stride
        self.Bneck1 = Bneck(channels, channels*2, 3, 2, True, 'relu',
                            self.allow_res)
        self.Bneck2 = Bneck(channels, channels*2, 3, 1, True, 'relu',
                            self.allow_res)
        self.Bneck3 = Bneck(channels, channels*2, 3, 1, True, 'relu',
                            self.allow_res)
        self.Bneck4 = Bneck(channels, channels*2, 3, 1, True, 'relu',
                            self.allow_res)
        self.Bneck5 = Bneck(channels, channels*2, 3, 1, True, 'relu',
                            self.allow_res)
        self.Bneck6 = Bneck(channels, channels*2, 3, 1, True, 'relu',
                            self.allow_res)

    def call(self, input):

        if self.do_initial_pool:
            x = tf.keras.layers.MaxPool2D(pool_size=(2, 2))(input)
            # print('[att] x: ', x.shape)
        else:
            x = input

        shape_adjusted = (int(x.shape[1])) % 2 == 1
        # print('[att] shape_adjusted: ', shape_adjusted)

        x = self.Bneck1(x)
        # print('[att] b1: ', x.shape)
        x = self.Bneck2(x)
        # print('[att] b2: ', x.shape)
        x = tf.keras.layers.MaxPool2D(pool_size=(2, 2))(x)
        x = self.Bneck3(x)
        # print('[att] b3: ', x.shape)
        x = self.Bneck4(x)
        x = tf.keras.layers.UpSampling2D(size=(2, 2))(x)
        # print('[att] b4: ', x.shape)
        x = self.Bneck5(x)
        # print('[att] b5: ', x.shape)
        x = self.Bneck6(x)
        # print('[att] b6: ', x.shape)

        x = tf.keras.layers.UpSampling2D(size=(2, 2))(x)

        if self.do_initial_pool:
            if shape_adjusted:
                cropped = ((1, 0), (1, 0))
                x = tf.keras.layers.Cropping2D(cropping=cropped)(x)
                # print('[att] x: ', x)
            x = tf.keras.layers.UpSampling2D(size=(2, 2))(x)

        # print('[att] x: ', x.shape)
        return tf.keras.backend.sigmoid(x) + 1.


class ResidualAttention(tf.keras.layers.Layer):
    def __init__(
            self,
            channels: int,
            do_initial_pool: bool,
            allow_res: bool,
            name: str = "ResidualAttention",
    ):
        super().__init__(name=name)

        self.do_initial_pool = do_initial_pool
        self.channels = channels
        self.allow_res = allow_res

        self.conv = ConvNormAct(
            channels,
            kernel_size=3,
            stride=1,
            padding=1,
            norm_layer="bn",
            act_layer="relu",
            use_bias=False,
            name="inputConv",
        )

        # out channels, exp channels, kernel, stride
        self.Bneck1 = Bneck(channels, channels*2, 3, 2, True, 'relu',
                            self.allow_res)
        self.Bneck2 = Bneck(channels, channels*2, 3, 1, True, 'relu',
                            self.allow_res)
        self.Bneck3 = Bneck(channels, channels*2, 3, 1, True, 'relu',
                            self.allow_res)
        self.Bneck4 = Bneck(channels, channels*2, 3, 1, True, 'relu',
                            self.allow_res)
        self.Bneck5 = Bneck(channels, channels*2, 3, 1, True, 'relu',
                            self.allow_res)
        self.Bneck6 = Bneck(channels, channels*2, 3, 1, True, 'relu',
                            self.allow_res)

    def call(self, input):

        if self.do_initial_pool:
            x = tf.keras.layers.MaxPool2D(pool_size=(2, 2))(input)
            # print('[att] x: ', x.shape)
        else:
            x = input

        shape_adjusted = (int(x.shape[1])) % 2 == 1
        # print('[att] shape_adjusted: ', shape_adjusted)

        Bneck1_out = self.Bneck1(x) 

        Bneck2_out = self.Bneck2(Bneck1_out)
        # print('[att] input: ', input.shape)
        # print('[att] bneck1: ', Bneck1_out.shape)
        # print('[att] bneck2: ', Bneck2_out.shape)
        x = tf.keras.layers.MaxPool2D(pool_size=(2, 2))(Bneck2_out)
        x = self.Bneck3(x)
        x = self.Bneck4(x)
        x = tf.keras.layers.UpSampling2D(size=(2, 2))(x)

        # print('[att] b4: ', x.shape)
        x = self.Bneck5(x + Bneck2_out)
        # print('[att] b5: ', x.shape)
        x = self.Bneck6(x + Bneck1_out)
        # print('[att] b6: ', x.shape)

        x = tf.keras.layers.UpSampling2D(size=(2, 2))(x)

        if self.do_initial_pool:
            if shape_adjusted:
                cropped = ((1, 0), (1, 0))
                x = tf.keras.layers.Cropping2D(cropping=cropped)(x)
                # print('[att] x: ', x)
            x = tf.keras.layers.UpSampling2D(size=(2, 2))(x)  # 64

        # print('[att] x: ', x.shape)
        return tf.keras.backend.sigmoid(x) + 1.