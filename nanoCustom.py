import Live
from _Framework.Control import ButtonControl
from _Framework.DeviceComponent import DeviceComponent as DeviceComponentBase

class MyCustomComponent(DeviceComponentBase):
    unmute_all_button = ButtonControl()
    toggle_view_button = ButtonControl()
    prev_device_button = ButtonControl()
    next_device_button = ButtonControl()
    dev_reset_button = ButtonControl()

    @unmute_all_button.pressed
    def unmute_all_button(self, button):
        for t in (tuple(self.song().tracks) + tuple(self.song().return_tracks)):
            if t.mute:
                t.mute = 0

    @toggle_view_button.pressed
    def toggle_view_button(self, button):
        self.application().view.show_view('Detail')
        if self.application().view.is_view_visible('Detail/Clip'):
            self.application().view.show_view('Detail/DeviceChain')
        else:
            self.application().view.show_view('Detail/Clip')

    @prev_device_button.pressed
    def prev_device_button(self, button):
        self._scroll_device_view(Live.Application.Application.View.NavDirection.left)

    @next_device_button.pressed
    def next_device_button(self, button):
        self._scroll_device_view(Live.Application.Application.View.NavDirection.right)

    def _scroll_device_view(self, direction):
        self.application().view.show_view('Detail')
        self.application().view.show_view('Detail/DeviceChain')
        self.application().view.scroll_view(direction, 'Detail/DeviceChain', False)

    @dev_reset_button.pressed
    def dev_reset_button(self, button):
        tracks = tuple(self.song().tracks) + tuple(self.song().return_tracks) + (self.song().master_track,)
        for t in tracks:
            for d in t.devices:
                if d.name.startswith('RESET'):
                    self.reset_device(d)

    def reset_device(self, device):
        for p in device.parameters:
            if p and p.is_enabled and not p.is_quantized and p.name != 'Chain Selector':
                p.value = 0

# Add your custom actions here