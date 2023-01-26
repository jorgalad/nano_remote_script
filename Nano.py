from __future__ import absolute_import, print_function, unicode_literals
import Live
from builtins import range
from _Framework.ControlSurface import ControlSurface
from _Framework.TransportComponent import TransportComponent
from _Framework.MixerComponent import MixerComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.EncoderElement import EncoderElement
from _Framework.Layer import Layer
from _Framework.ModesComponent import AddLayerMode, ModesComponent, LayerMode
from _Framework.SessionComponent import SessionComponent
from _Framework.SliderElement import SliderElement
from _Framework.SubjectSlot import subject_slot
from _Framework.DeviceComponent import DeviceComponent

# Local Imports
from .nanoCustom import MyCustomComponent
from .MIDI_map import *

# 0 = Note
# 1 = CC
# 0 = non_momentary
# 1 = is_momentary

class Nano(ControlSurface):  # Create a class
    __module__ = __name__  # Name it
    __doc__ = "Nano Controller Script function"  # Doc string

    def __init__(self, c_instance):  # Init the class
        ControlSurface.__init__(self, c_instance)  # Import CS components
        self.msg_test()
        with self.component_guard():  # Context manager whichs guards user code. Prevents unnecesary updating and enables several optimisations
            self._create_controls()
            self._create_mixer()
            self._create_session()
            self._create_transport()
            self._create_device()
            self._create_custom()
            self._create_modes()

    def _create_controls(self):
        def make_button(identifier, name, midi_type=1): # Was 1
            self.log_message('Creating %s, identifier %s' % (name, identifier))
            return ButtonElement(is_momentary=True, msg_type=midi_type, channel=chan, identifier=identifier, name=name)

        def make_encoder(identifier, name):
            return EncoderElement(1, chan, identifier, Live.MidiMap.MapMode.absolute, name=name)

        def make_slider(identifier, name):
            return SliderElement(1, chan, identifier, name=name)

        self._faders = ButtonMatrixElement(rows=[
            [make_slider(0 + i, 'Volume_%d' % (i + 1)) for i in range(8)]])

        self._solo_buttons = ButtonMatrixElement(rows=[
            [make_button(32 + i, 'Solo_%d' % (i + 1)) for i in range(8)]])
        self._mute_buttons = ButtonMatrixElement(rows=[
            [make_button(48 + i, 'Mute_%d' % (i + 1)) for i in range(8)]])
        self._arm_buttons = ButtonMatrixElement(rows=[
            [make_button(64 + i, 'Mute_%d' % (i + 1)) for i in range(8)]])

        self._encoders = ButtonMatrixElement(rows=[
            [make_encoder(16 + i, 'Pan_Device_%d' % (i + 1)) for i in range(8)]])

        self._up_button = make_button(62, 'Up')
        self._down_button = make_button(61, 'Down')

        self._track_left_btn = make_button(58, 'Track_Left')
        self._track_right_btn = make_button(59, 'Track_Right')

        self._rewind_btn = make_button(43, 'Rewind')
        self._forward_btn = make_button(44, 'Forward')

        self._loop_button = make_button(46, 'Cycle')
        self._set_button = make_button(60, 'Set')
        self._stop_button = make_button(42, 'Stop')

        # MODE BUTTONS
        self._regular_mode_button = make_button(41, 'Regular_Mode_Button')
        self._api_mode_button = make_button(45, 'API_Mode_Button')

    def msg_test(self):
        self.log_message('======================= Oh hi! ======================= ')
        self.show_message('Hello from Nano Remote Script')

    def _create_session(self):
        self.log_message('======================= Session Created ======================= ')
        self._session = SessionComponent(num_tracks=num_tracks, num_scenes=num_scenes, is_enabled=True, auto_name=True)
        self.set_highlighting_session_component(self._session)
        self._session.set_track_bank_buttons(self._track_right_btn, self._track_left_btn)
        self._session.set_scene_bank_buttons(self._up_button, self._down_button)
        self._session.scene(0).set_launch_button(self._rewind_btn)
        self._session.scene(1).set_launch_button(self._forward_btn)
        self._session.set_stop_all_clips_button(self._stop_button)
        self._on_session_offset_changed.subject = self._session

    def _create_transport(self):
        self.log_message('======================= Transport Created ======================= ')
        self._transport = TransportComponent(self)
        self._transport.set_loop_button(self._loop_button)
        self._transport.set_metronome_button(self._set_button)

    def _create_device(self):
        self._device = DeviceComponent(name='Device_Component', is_enabled=True,
                                       device_selection_follows_track_selection=True)

    def _create_mixer(self):
        self._mixer = MixerComponent(num_tracks, name='Mixer')
        self.song().view.selected_track = self._mixer.channel_strip(0)._track  # Make sure we see the first track
        self._mixer.set_volume_controls(self._faders)

    def _create_custom(self):
        self._custom = MyCustomComponent()

    def _create_modes(self):
        self._modes = ModesComponent(name='Encoder_Modes')
        self._modes.add_mode('regular_mode', LayerMode(self._mixer, Layer(pan_controls=self._encoders,
                                                                          solo_buttons=self._solo_buttons,
                                                                          mute_buttons=self._mute_buttons,
                                                                          arm_buttons=self._arm_buttons)))
        self._modes.add_mode('api_mode', (
            AddLayerMode(self._device, Layer(parameter_controls=self._encoders,
                                             on_off_button=self._solo_buttons[6])),

            AddLayerMode(self._transport, Layer(record_button=self._solo_buttons[0],
                                                tap_tempo_button=self._solo_buttons[1])),

            AddLayerMode(self._session, Layer(clip_launch_buttons=self._mute_buttons)),

            AddLayerMode(self._mixer, Layer(track_select_buttons=self._arm_buttons)),

            AddLayerMode(self._custom, Layer(unmute_all_button=self._solo_buttons[2],
                                             toggle_view_button=self._solo_buttons[3],
                                             prev_device_button=self._solo_buttons[4],
                                             next_device_button=self._solo_buttons[5],
                                             dev_reset_button=self._solo_buttons[7]))))

        self._modes.layer = Layer(regular_mode_button=self._regular_mode_button,
                                  api_mode_button=self._api_mode_button)

        self._modes.selected_mode = 'regular_mode'
        self._on_selected_mode.subject = self._modes

    # Listeners
    # Check if the mode has changed
    @subject_slot('selected_mode')
    def _on_selected_mode(self, mode):
        if mode == 'regular_mode':
            self.show_message('Regular Mode')
        else:
            self.show_message('API Mode')

    # When the session box moves, show which tracks we're controlling
    @subject_slot('offset')
    def _on_session_offset_changed(self):
        session = self._on_session_offset_changed.subject
        self._show_controlled_tracks_message(session)

    def _show_controlled_tracks_message(self, session):
        start = session.track_offset() + 1
        end = min(start + 8, len(session.tracks_to_use()))
        if start < end:
            self.show_message('Controlling Track %d to %d' % (start, end))
        else:
            self.show_message('Controlling Track %d' % start)
