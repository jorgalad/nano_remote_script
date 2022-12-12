from __future__ import absolute_import, print_function, unicode_literals
import Live
# from __future__ import absolute_import, print_function, unicode_literals
# #from __future__ import with_statement                           # Necessary for Live 9 Compatibility
from _Framework.ControlSurface import ControlSurface

# from _Framework.SessionComponent import SessionComponent
from _Framework.TransportComponent import TransportComponent
from _Framework.MixerComponent import MixerComponent
# from _Framework.DeviceComponent import DeviceComponent
#
# from _Framework.ModesComponent import AddLayerMode, ModeButtonBehaviour, ModesComponent
#
# import _Framework.Layer as Layer
#
#







from builtins import chr, map, range
from functools import partial
from itertools import chain

from _Framework import Task
from _Framework.ButtonElement import ButtonElement
import _Framework.ButtonMatrixElement as ButtonMatrixElement
import _Framework.EncoderElement as EncoderElement
import _Framework.IdentifiableControlSurface as IdentifiableControlSurface
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.Layer import Layer
from _Framework.ModesComponent import AddLayerMode, ModeButtonBehaviour, ModesComponent
import _Framework.SessionComponent as SessionComponent
from _Framework.SliderElement import SliderElement
from _Framework.SubjectSlot import subject_slot
from _Framework.Util import nop
#from .ButtonElement import ButtonElement
#from .DeviceComponent import DeviceComponent, DeviceModeComponent
#from .MixerComponent import MixerComponent
#from .SkinDefault import make_biled_skin, make_default_skin




from functools import partial
from itertools import chain
from .MIDI_map import *


import time
# 0 = Note
# 1 = CC
# 0 = non_momentary
# 1 = is_momentary


# Check 'Launch Controls XL' scripts
# Copy Framework Directory into this one
#
class Nano(ControlSurface):                                     # Create a class
    __module__ = __name__                                       # Name it
    __doc__ = "Nano Controller Script function"                               # Doc string

    def __init__(self, c_instance):                             # Init the class
        ControlSurface.__init__(self, c_instance)               # Import CS components
        self.msg_test()
        with self.component_guard():                            # Context manager whichs guards user code. Prevents unnecesary updating and enables several optimisations
            self._create_controls()                             # Make Button, Slider, Encoders
    #        self.setup_session_control()
     #       self.setup_transport_control()

        self._initialize_task = self._tasks.add(Task.sequence(Task.wait(1), Task.run(self._create_components)))
        self._initialize_task.kill()

    def _create_components(self):
        self._initialize_task.kill()
        self._disconnect_and_unregister_all_components()
        with self.component_guard():
            mixer = self._create_mixer()
            session = self._create_session()
            #device = self._create_device()
            session.set_mixer(mixer)
            #self.set_device_component(device)


    # _ underscore means it's being called from within the class
    def _create_controls(self):
        def make_button(identifier, name, midi_type=1):
            self.log_message('Creating %s, identifier %s' % (name, identifier))
            return ButtonElement(is_momentary=True, msg_type=midi_type, channel=chan, identifier=identifier, name=name)

        def make_encoder(identifier, name):
            return EncoderElement(1,chan,identifier,Live.MidiMap.MapMode.absolute,name=name)

        # def make_slider(identifier, name, midi_type=1):
        #     return SliderElement(is_momentary=True, msg_type=midi_type, channel=chan, identifier=identifier, name=name)
        #
        def make_slider(identifier, name):
            return SliderElement(1, chan, identifier, name=name)

        def make_button_list(identifiers, name):
            return [make_button(identifier, name % (i + 1), 0) for i, identifier in enumerate(identifiers)]

        self._volume_faders = ButtonMatrixElement(rows=[
            [make_slider(0 + i, 'Volume_%d' % (i + 1)) for i in range(8)]])

        #self._master_fader = make_slider(67, "Master_Fader")
        #self._master_encoders = ButtonMatrixElement(
        #    rows=[[make_encoder(i, "Master_Knob_%d" % (i / 9)) for i in [8, 17, 26]]])

        self._left_button = make_button(80, 'Track_Left') #Name is probably not super necesarry but fancy
        self._right_button = make_button(81, 'Track_Right')
        self._shift_button = make_button(82, 'Shift')


        #self._send_encoders = ButtonMatrixElement(rows=[
        # [make_encoder(13 + i, 'Top_Send_%d' % (i + 1)) for i in range(8)],
        # [make_encoder(29 + i, 'Bottom_Send_%d' % (i + 1)) for i in range(8)]])

        #self._pan_device_encoders = ButtonMatrixElement(rows=[
        # [make_encoder(49 + i, 'Pan_Device_%d' % (i + 1)) for i in range(8)]])

        #self._volume_faders = ButtonMatrixElement(rows=[
        # [make_slider(0 + i, 'Volume_%d' % (i + 1)) for i in range(8)]])

        self._volume_faders = None
        self._pan_device_mode_button = make_button(105, 'Pan_Device_Mode', 0)
        self._mute_mode_button = make_button(106, 'Mute_Mode', 0)
        self._solo_mode_button = make_button(107, 'Solo_Mode', 0)
        self._arm_mode_button = make_button(108, 'Arm_Mode', 0)
        self._up_button = make_button(61, 'Up')
        self._down_button = make_button(62, 'Down')
        self._left_button = make_button(106, 'Track_Left')
        self._right_button = make_button(107, 'Track_Right')



        # self._select_buttons = ButtonMatrixElement(rows=[
        #  make_button_list(chain(range(41, 45), range(57, 61)), 'Track_Select_%d')])
        # self._state_buttons = ButtonMatrixElement(rows=[
        #  make_button_list(chain(range(73, 77), range(89, 93)), 'Track_State_%d')])
        #

        #self._send_encoder_lights = ButtonMatrixElement(rows=[
        # make_button_list([
        #  13, 29, 45, 61, 77, 93, 109, 125], 'Top_Send_Encoder_Light_%d'),
        # make_button_list([
        #  14, 30, 46, 62, 78, 94, 110, 126], 'Bottom_Send_Encoder_Light_%d')])
        #self._pan_device_encoder_lights = ButtonMatrixElement(rows=[
        # make_button_list([
        #  15, 31, 47, 63, 79, 95, 111, 127], 'Pan_Device_Encoder_Light_%d')])


    def msg_test(self):
        self.log_message('======================= Hi! ======================= ')
        self.show_message('Hello..')

    def _create_session(self):
        session = SessionComponent(num_tracks=num_tracks,
                                num_scenes=num_scenes,
                                is_enabled=True,
                                auto_name=True,
                                enable_skinning=True)
        session.layer = Layer(track_bank_left_button=(self._left_button),
          track_bank_right_button=(self._right_button))
        self.set_highlighting_session_component(self.Session)
        self._on_session_offset_changed.subject = session
        return session


    def setup_session_control(self):
        self.show_message("#################### SESSION: ON ##############################")
        self.Session = SessionComponent(num_tracks, num_scenes)  # here we create a session called Session
        self.Session.set_offsets(0, 0)  # offset start a the up-left corner (track1,row1)
        self.Session._do_show_highlight()  # to ensure that this session will be highlighted
        self.set_highlighting_session_component(self.Session)
        self.Session.set_scene_bank_buttons(ButtonElement(1, 1, GC, sesDown),ButtonElement(1, 1, GC, sesUp))
        self.Session.set_stop_all_clips_button(ButtonElement(1, 1, GC, 42))

    def setup_transport_control(self):
        self.transport = TransportComponent(self)
        self.transport.set_loop_button(ButtonElement(1, 1, GC, cycleOn))


    def _create_device(self):
        device = DeviceComponent(name='Device_Component',
          is_enabled=False,
          device_selection_follows_track_selection=True)
        device.layer = Layer(parameter_controls=(self._pan_device_encoders),
          parameter_lights=(self._pan_device_encoder_lights),
          priority=1)
        device_settings_layer = Layer(bank_buttons=(self._state_buttons),
          prev_device_button=(self._left_button),
          next_device_button=(self._right_button),
          priority=1)
        mode = DeviceModeComponent(component=device,
          device_settings_mode=[
         AddLayerMode(device, device_settings_layer)],
          is_enabled=True)
        mode.layer = Layer(device_mode_button=(self._pan_device_mode_button))
        return device


    # def setup_mixer_control(self):
    #     self.mixer = MixerComponent(num_tracks, 0, False, False)
    #     self.mixer.name = 'Mixer'
    #     self.mixer.set_track_offset(0)
    #     self.show_message("#################### MIXER CONTROL ##############################")
    #
    #     for index in range(num_tracks):
    #         strip = self.mixer.channel_strip(index)
    #         strip.name = 'Mixer_ChannelStrip_' + str(index)
    #         strip.set_volume_control(SliderElement(1, GC, mixVol[index]))
    #         strip._invert_mute_feedback = True

    def _create_mixer(self):
        mixer = MixerComponent(num_tracks, is_enabled=True, auto_name=True)
        mixer.layer = Layer(
          #send_controls=(self._send_encoders),
          next_sends_button=(self._down_button),
          prev_sends_button=self._up_button,
          #pan_controls=(self._pan_device_encoders),
          volume_controls=self._volume_faders
                            )
        mixer.on_send_index_changed = partial(self._show_controlled_sends_message, mixer)
        for channel_strip in map(mixer.channel_strip, range(num_tracks)):
            channel_strip.empty_color = 'Mixer.NoTrack'

        mixer_modes = ModesComponent()
        mixer_modes.add_mode('mute', [AddLayerMode(mixer, Layer(mute_buttons=(self._state_buttons)))])
        mixer_modes.add_mode('solo', [AddLayerMode(mixer, Layer(solo_buttons=(self._state_buttons)))])
        mixer_modes.add_mode('arm', [AddLayerMode(mixer, Layer(arm_buttons=(self._state_buttons)))])
        mixer_modes.layer = Layer(mute_button=(self._mute_mode_button),
          solo_button=(self._solo_mode_button),
          arm_button=(self._arm_mode_button))
        mixer_modes.selected_mode = 'mute'
        return mixer

