#!/usr/bin/env python
import gtk

from kiwi.ui.delegates import GladeDelegate, GladeGladeSlaveDelegate
from kiwi.ui.gadgets import quit_if_last


class NestedSlave(GladeGladeSlaveDelegate):
    def __init__(self, parent):
        self.parent = parent
        GladeGladeSlaveDelegate.__init__(self, gladefile="slave_view2",
                                    toplevel_name="window_container",
                                    widgets=["slave_view2"])


# This slave will be attached to the toplevel view, and will contain another
# slave
class TestSlave(GladeGladeSlaveDelegate):
    def __init__(self, parent):
        self.parent = parent
        # Be carefull that, when passing the widget list, the sizegroups
        # that you want to be merged are in the list, otherwise, they wont
        # be.
        GladeGladeSlaveDelegate.__init__(self, gladefile="slave_view",
                                    toplevel_name="window_container",
                                    widgets=["slave_view", "sizegroup1"])

        self.slave = NestedSlave(self)
        self.attach_slave("eventbox", self.slave)
        self.slave.show()
        self.slave.focus_toplevel() # Must be done after attach

class Shell(GladeDelegate):
    def __init__(self):
        GladeDelegate.__init__(self, gladefile="shell",
                               delete_handler=quit_if_last)

        self.slave = TestSlave(self)
        self.attach_slave("placeholder", self.slave)
        self.slave.show()
        self.slave.focus_toplevel() # Must be done after attach

    def on_ok__clicked(self, *args):
        self.hide_and_quit()

shell = Shell()
shell.show()

gtk.main()

