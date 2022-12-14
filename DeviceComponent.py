from __future__ import absolute_import, print_function, unicode_literals
from _Framework.Control import ButtonControl, control_list
from _Framework.DeviceComponent import DeviceComponent as DeviceComponentBase

class DeviceComponent(DeviceComponentBase):
    dev_reset_button = ButtonControl(color='DefaultButton.On')
    loop_start_button = ButtonControl(color='DefaultButton.On')

    @dev_reset_button.pressed
    def dev_reset_button(self, button):
        self._device_reset()

    @loop_start_button.pressed
    def dev_reset_button(self, button):
        self._loop_start()

    def _device_reset(self):
        tracks = tuple(self.song().tracks) + tuple(self.song().return_tracks) + (self.song().master_track,)
        for t in tracks:
            for d in t.devices:
                if d.name.startswith('RESET'):
                    for p in d.parameters:
                        if p and p.is_enabled and not p.is_quantized and p.name != 'Chain Selector':
                            p.value = 0

    def loop_start(self):
        pass



