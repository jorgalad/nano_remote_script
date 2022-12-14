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
            #self._create_device()
            self._create_modes()

    # _ underscore means it's being called from within the class
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

        #self._dev_mode_button = make_button(60, 'Shift', 0)
        #self._pan_mode_button = make_button(41, 'Pan', 0)
        # MODE BUTTONS
        self._volume_mode_button = make_button(41, 'Volume_Mode_Button')
        self._pan_mode_button = make_button(45, 'Pan_Mode_Button')

        #self._pan_device_mode_button = make_button(60, 'Pan_Device_Mode', 0)
        #self._mute_mode_button = make_button(48, 'Mute_Mode', 0)
        #self._arm_mode_button = make_button(64, 'Arm_Mode', 0)

        self._state_buttons = ButtonMatrixElement(rows=[
          make_button_list(chain(range(73, 77), range(89, 93)), 'Track_State_%d')])

        #self._state_buttons = ButtonMatrixElement(rows=[
        #    make_button_list(range(73, 77)), 'Track_State_%d')]
        #self._state_buttons = ButtonMatrixElement(rows=[
        #    [make_button(64 + i, 'Mute_%d' % (i + 1)) for i in range(8)]])


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
        self.log_message('======================= Device Created ======================= ')
        device = DeviceComponent(name='Device_Component', is_enabled=False, device_selection_follows_track_selection=True)
        device.layer = Layer(parameter_controls=(self._pan_device_encoders), priority=1)
        device_settings_layer = Layer(bank_buttons=(self._state_buttons),
          prev_device_button=(self._dev_left_btn),
          next_device_button=(self._dev_right_btn),
          priority=1)
        mode = DeviceModeComponent(component=device,
         device_settings_mode=[
        AddLayerMode(device, device_settings_layer)],
         is_enabled=True)
        mode.layer = Layer(device_mode_button=(self._pan_device_mode_button))
        return device

    def _create_mixer(self):
        # self._session_ring = SessionRingComponent(num_tracks=(self._encoders.width()),
        #   num_scenes=0,
        #   is_enabled=False,
        #   name='Session_Ring')
        # self._mixer = MixerComponent(tracks_provider=(self._session_ring), name='Mixer')
        self._mixer = MixerComponent(num_tracks, name='Mixer')

    def _create_mixer_2(self):
        self.mixer = MixerComponent(num_tracks, is_enabled=True, auto_name=True)
        #mixer.next_track_button = self._track_right_btn
        #mixer.prev_track_button = self._track_left_btn
        self.mixer.set_select_buttons(self._track_right_btn, self._track_left_btn)
        self.mixer.layer = Layer(
          solo_buttons=self._solo_buttons,
          mute_buttons=self._mute_buttons,
          arm_buttons=self._arm_buttons,
          pan_controls=self._pan_device_encoders,
          #volume_controls=self._volume_faders
                            )
        #mixer.on_send_index_changed = partial(self._show_controlled_sends_message, mixer)
        for channel_strip in map(self.mixer.channel_strip, range(num_tracks)):
            channel_strip.empty_color = 'Mixer.NoTrack'



        # mixer_modes = ModesComponent()
        # mixer_modes.add_mode('mute', [AddLayerMode(mixer, Layer(mute_buttons=(self._state_buttons)))])
        # mixer_modes.add_mode('solo', [AddLayerMode(mixer, Layer(solo_buttons=(self._state_buttons)))])
        # mixer_modes.add_mode('arm', [AddLayerMode(mixer, Layer(arm_buttons=(self._state_buttons)))])
        # mixer_modes.layer = Layer(
        #   mute_button=(self._mute_mode_button),
        #   solo_button=(self._solo_mode_button),
        #   arm_button=(self._arm_mode_button)),
        # mixer_modes.selected_mode = 'solo'


        return self.mixer


    def _create_modes(self):
        self._modes = ModesComponent(name='Encoder_Modes')
        self._modes.add_mode('volume_mode', LayerMode(self._mixer, Layer(volume_controls=(self._volume_faders))))
        self._modes.add_mode('pan_mode', LayerMode(self._mixer, Layer(pan_controls=(self._volume_faders))))
        self._modes.layer = Layer(volume_mode_button=(self._volume_mode_button),
                                  pan_mode_button=(self._pan_mode_button))
        self._modes.selected_mode = 'volume_mode'
