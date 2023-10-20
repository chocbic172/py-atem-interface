from interfacegen import InterfaceGenerator
import os

PROTOCOL_DIR = os.path.join(os.getcwd(), 'protocol')
OUTPUT_DIR = os.path.join(os.getcwd(), 'interface')


if __name__ == "__main__":
    generator = InterfaceGenerator(PROTOCOL_DIR)
    generator.generate_interface(OUTPUT_DIR)
