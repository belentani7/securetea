import os
import tensorflow as tf
import numpy as np

class DetectDDoS:
    
    """
    Class responsible for dectecting DDoS that uses Bidirections LSTM classifier and also predict
    the class of live features from the incoming request

    """
    
    def __init__(self, data):
        
        """

        A constructor that initialise the required variables
        
        Args: packet data
        Returns: None

        """
        
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'bidirection_lstm.h5')
        self.model = tf.keras.models.load_model(model_path)
        
        self.features = [ 'frame.len', 'ip.hdr_len',
                            'ip.len', 'ip.flags.rb', 'ip.flags.df', 'p.flags.mf', 'ip.frag_offset',
                            'ip.ttl', 'ip.proto', 'tcp.srcport', 'tcp.dstport',
                            'tcp.len', 'tcp.ack', 'tcp.flags.res', 'tcp.flags.ns', 'tcp.flags.cwr',
                            'tcp.flags.ecn', 'tcp.flags.urg', 'tcp.flags.ack', 'tcp.flags.push',
                            'tcp.flags.reset', 'tcp.flags.syn', 'tcp.flags.fin', 'tcp.window_size',
                            'tcp.time_delta']
        
    def predict(self):
        
        """
        A method that is responsible for predicting if the packet is a part of DDoS.

        Args: None
        Returns: prediction (1 or 0) = (DDoS or normal)


        """
        
        # TODO : processing of packets captured from asyncio
        
        packet = None
        
        if packet is None:
            return 0

        attack = self.model.predict(packet)
        
        if attack[0] > 5.0:
            return 1
        else:
            return 0