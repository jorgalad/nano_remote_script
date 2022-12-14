from __future__ import absolute_import, print_function, unicode_literals
import Live

from _Framework.ControlSurface import ControlSurface
from _Framework.TransportComponent import TransportComponent
from _Framework.MixerComponent import MixerComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.EncoderElement import EncoderElement
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.Layer import Layer
from _Framework.ModesComponent import AddLayerMode, ModeButtonBehaviour, ModesComponent, LayerMode
from _Framework.SessionComponent import SessionComponent #, SessionRingComponent
from _Framework.SliderElement import SliderElement
from _Framework.DeviceComponent import DeviceComponent
#from .ButtonElement import ButtonElement
#from .DeviceComponent import DeviceComponent, DeviceModeComponent

#from ableton.v2.control_surface.mode import LayerMode, ModesComponent

from builtins import chr, map, range
from functools import partial
from itertools import chain
from .MIDI_map import *

# 0 = Note
# 1 = CC
# 0 = non_momentary
# 1 = is_momentary

# Check 'Launch Controls XL' scripts
# Copy Framework Directory into this one

def getSong():
	"""Gets the current Song instance"""
	return Live.Application.get_application().get_document()


class Nano(ControlSurface):                                     # Create a class
    __module__ = __name__                                       # Name it
    __doc__ = "Nano Controller Script function"                 # Doc string
    def __init__(self, c_instance):                             # Init the class
        ControlSurface.__init__(self, c_instance)               # Import CS components
        self.msg_test()
        with self.component_guard():                            # Context manager whichs guards user code. Prevents unnecesary updating and enables several optimisations
            self._create_controls()                             # Make Button, Slider, Encoders
            self._create_transport()
            mixer = self._create_mixer()
            session = self._create_session()
            session.set_mixer(mixer)
            device = self._create_device()
            self._create_modes()
            self.set_device_component(device)

    def _create_controls(self):
        def make_button(identifier, name, midi_type=1):
            self.log_message('Creating %s, identifier %s' % (name, identifier))
            return ButtonElement(is_momentary=True, msg_type=midi_type, channel=chan, identifier=identifier, name=name)

        def make_encoder(identifier, name):
            return EncoderElement(1,chan,identifier,Live.MidiMap.MapMode.absolute,name=name)

        def make_slider(identifier, name):
            return SliderElement(1, chan, identifier, name=name)

        def make_button_list(identifiers, name):
            return [make_button(identifier, name % (i + 1), 0) for i, identifier in enumerate(identifiers)]

        self._volume_faders = ButtonMatrixElement(rows=[
            [make_slider(0 + i, 'Volume_%d' % (i + 1)) for i in range(8)]])

        self._solo_buttons = ButtonMatrixElement(rows=[
            [make_button(32 + i, 'Solo_%d' % (i + 1)) for i in range(8)]])
        self._mute_buttons = ButtonMatrixElement(rows=[
            [make_button(48 + i, 'Mute_%d' % (i + 1)) for i in range(8)]])
        self._arm_buttons = ButtonMatrixElement(rows=[
            [make_button(64 + i, 'Mute_%d' % (i + 1)) for i in range(8)]])

        self._pan_device_encoders = ButtonMatrixElement(rows=[
            [make_encoder(16 + i, 'Pan_Device_%d' % (i + 1)) for i in range(8)]])

        self._ses_left_button = make_button(58, 'Session_Left')
        self._ses_right_button = make_button(59, 'Session_Right')
        self._up_button = make_button(62, 'Up')
        self._down_button = make_button(61, 'Down')

        self._track_left_btn = make_button(43, 'Track_Left')
        self._track_right_btn = make_button(44, 'Track_Right')

        self._dev_left_btn = make_button(43, 'Dev_Left')
        self._dev_right_btn = make_button(44, 'Dev_Right')
        self._loop_button = make_button(46, 'Cycle')

        # MODE BUTTONS
        self._volume_mode_button = make_button(41, 'Volume_Mode_Button')
        self._device_mode_button = make_button(45, 'Device_Mode_Button')

        self._state_buttons = ButtonMatrixElement(rows=[
          make_button_list(chain(range(73, 77), range(89, 93)), 'Track_State_%d')])


    def msg_test(self):
        self.log_message('======================= Oh hi! ======================= ')
        self.show_message('Hello..')

    def _create_session(self):
        self.log_message('======================= Session Created ======================= ')
        self.log_message(getSong())
        session = SessionComponent(num_tracks=num_tracks,
                                num_scenes=num_scenes,
                                is_enabled=True,
                                auto_name=True)
        session.layer = Layer(track_bank_left_button=(self._ses_left_button),
                              track_bank_right_button=(self._ses_right_button))
        self.set_highlighting_session_component(session)
        session.set_scene_bank_buttons(self._up_button, self._down_button)
        return session

    def _create_transport(self):
        self.log_message('======================= Transport Created ======================= ')
        self.transport = TransportComponent(self)
        self.transport.set_loop_button(self._loop_button)

    def _create_device(self):
        self._device = DeviceComponent(name='Device_Component', is_enabled=True, device_selection_follows_track_selection=True)
        #device.layer = Layer(parameter_controls=(self._pan_device_encoders), priority=1)
        #device_settings_layer = Layer(bank_buttons=(self._state_buttons),
        #  prev_device_button=(self._left_button),
        #  next_device_button=(self._right_button),
        #  priority=1)
        #mode = DeviceModeComponent(component=device,
        #  device_settings_mode=[
        # AddLayerMode(device, device_settings_layer)],
        #  is_enabled=True)
        #mode.layer = Layer(device_mode_button=(self.device_mode_button))
        #return device

    def _create_mixer(self):
        self._mixer = MixerComponent(num_tracks, name='Mixer')
        self.song().view.selected_track = self._mixer.channel_strip(0)._track       # Make sure we see the first track
        self._mixer.set_arm_buttons(self._arm_buttons)
        self._mixer.set_solo_buttons(self._solo_buttons)
        self._mixer.set_mute_buttons(self._mute_buttons)


    def _create_modes(self):
        self._modes = ModesComponent(name='Encoder_Modes')
        self._modes.add_mode('volume_mode', LayerMode(self._mixer, Layer(volume_controls=(self._volume_faders))))
        self._modes.add_mode('device_mode', LayerMode(self._device, Layer(parameter_controls=(self._volume_faders))))

        #self._modes.add_mode('pan_mode', LayerMode(self._mixer, Layer(pan_controls=(self._volume_faders))))
        self._modes.layer = Layer(volume_mode_button=(self._volume_mode_button),
                                  #pan_mode_button=(self._pan_mode_button),
                                  device_mode_button=(self._device_mode_button),
                                  )
        self._modes.selected_mode = 'volume_mode'
