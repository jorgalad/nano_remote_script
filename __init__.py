# Import main program
from __future__ import absolute_import, print_function, unicode_literals
from .Nano import Nano

def create_instance(c_instance):                    # Create an instance of the midi remote script
    return Nano(c_instance)                     # Call the function


