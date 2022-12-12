                       # Import main program
from __future__ import absolute_import, print_function, unicode_literals
import _Framework.Capabilities as caps
from .Nano import Nano

def get_capabilities():
    return {caps.CONTROLLER_ID_KEY: caps.controller_id(vendor_id=7285,
                                                       product_ids=[518],
                                                       model_name=['Arturia BeatStep']),

            caps.PORTS_KEY: [
                caps.inport(props=[caps.NOTES_CC, caps.SCRIPT, caps.REMOTE]),
                caps.outport(props=[caps.SCRIPT])]}






def create_instance(c_instance):                    # Create an instance of the midi remote script
    return Nano(c_instance)                     # Call the function


