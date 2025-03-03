import numpy as np
from gan_generator import GANGenerator
import tensorflow as tf

def quick_train():
    # Match dimensions: 5 input features, 15 output features
    input_shape = 5
    output_shape = 15
    
    # Generate training data
    num_samples = 1000
    X = np.random.normal(0, 1, (num_samples, input_shape))
    Y = np.random.normal(0, 1, (num_samples, output_shape))
    
    # Initialize and compile
    gan = GANGenerator()
    gan.generator.compile(loss='mse', optimizer='adam')
    
    # Train with reduced verbosity
    gan.generator.fit(X, Y, epochs=10, batch_size=32, verbose=1)
    
    # Save weights
    gan.generator.save_weights('gan_weights.h5')
    print("Training completed. Weights saved.")

if __name__ == "__main__":
    # Suppress TensorFlow warnings
    tf.get_logger().setLevel('ERROR')
    quick_train()