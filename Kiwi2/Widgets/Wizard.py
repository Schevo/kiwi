# -*- coding: iso-8859-1 -*-

from Kiwi2.initgtk import gtk, quit_if_last
from Kiwi2.Delegates import Delegate


class WizardStep:
    """ This class must be inherited by the steps """
    def __init__(self, previous=None, header=None):
        self.previous = previous
        self.header = header

    def post_init(self):
        # This is a virtual method, which must be redefined on children 
        # classes, if applicable.
        pass
    
    def next_step(self):
        # This is a virtual method, which must be redefined on children 
        # classes. It should not be called by the last step (in this case,
        # has_next_step should return 0).
        raise NotImplementedError
       
    def has_next_step(self):
        # This method should return False on last step classes
        return True

    def has_previous_step(self): 
        # This method should return False on first step classes; since
        # self.previous is normally None for them, we can get away with
        # this simplified check. Redefine as necessary.
        return self.previous is not None

    def previous_step(self):
        return self.previous

class PluggableWizard(Delegate):
    """ Wizard controller and view class """
    #gladefile = 'Wizard'
    #widgets = ['message',
               #'header',
               #'top_separator',
               #'cancel_button',
               ###'finish_button',
               #'back_button',
               #'next_button']
    retval = None
    def __init__(self, title, first_step, size=None):
        #_AbstractDialog.__init__(self, delete_handler=self.cancel)
        self._create_gui()
        Delegate.__init__(self, delete_handler=quit_if_last, toplevel=self.wizard)
        self.set_title(title)
        self.first_step = first_step
        if size:
            self.get_toplevel().set_default_size(size[0], size[1])
        self.change_step(first_step)

    def _create_gui(self):
        self.next_btn = gtk.Button(stock=gtk.STOCK_GO_FORWARD)
        self.next_btn.set_use_stock(True)
        self.previous_btn = gtk.Button(stock=gtk.STOCK_GO_BACK)
        self.previous_btn.set_use_stock(True)
        self.cancel_btn = gtk.Button(stock=gtk.STOCK_CANCEL)
        self.cancel_btn.set_use_stock(True)
        
        self.message_lbl = gtk.Label("message")
        self.header_lbl = gtk.Label("header")
        
        cancel_btn_hbox = gtk.HButtonBox()
        cancel_btn_hbox.pack_start(self.cancel_btn)
        cancel_btn_hbox.set_spacing(10)
        cancel_btn_hbox.set_border_width(15)
        cancel_btn_hbox.set_layout('start')
        
        prev_next_btns_hbox = gtk.HButtonBox()
        prev_next_btns_hbox.pack_start(self.previous_btn)
        prev_next_btns_hbox.pack_start(self.next_btn)
        prev_next_btns_hbox.set_spacing(10)
        prev_next_btns_hbox.set_border_width(15)
        prev_next_btns_hbox.set_layout('end')
        
        self.wizard_slave_ev = gtk.EventBox()
        btns_hbox = gtk.HBox()
        btns_hbox.pack_start(cancel_btn_hbox)
        btns_hbox.pack_start(prev_next_btns_hbox)
        
        vbox = gtk.VBox()
        vbox.pack_start(self.header_lbl)
        vbox.pack_start(self.wizard_slave_ev)
        vbox.pack_start(btns_hbox)
        vbox.pack_start(self.message_lbl)
        vbox.set_child_packing(self.header_lbl, expand=False, fill=True, 
                               padding=0, pack_type='start')
        vbox.set_child_packing(self.message_lbl, expand=False, fill=True, 
                               padding=0, pack_type='start')
        vbox.set_child_packing(btns_hbox, expand=False, fill=True, 
                               padding=0, pack_type='start')
        
        self.wizard = gtk.Window()
        self.wizard.add(vbox)
        
    def change_step(self, step):
        if step is None:
            # Sometimes for different reasons the wizard needs to be
            # interrupted. In this case, next/previous_step should return
            # None to get the wizard interrupted. self.cancel is called
            # because it is the most secure action to do, since interrupt
            # here does not mean success
            return self.cancel()
        self.attach_slave('wizard_slave_ev', step)
        self.current = step
        if step.header:
            self.header_lbl.show()
            #self.top_separator.show()
            self.header_lbl.set_text(step.header)
        else:
            self.header_lbl.hide()
            #self.top_separator.hide()
        self.update_view()
        self.current.post_init()
        return None

    def update_view(self): 
        # First page
        if not self.current.has_previous_step():
            self.enable_next()
            self.disable_back()
            self.disable_finish()
            self.message_lbl.hide()
        # Middle page
        elif self.current.has_next_step(): 
            self.enable_back()
            self.enable_next()
            self.disable_finish()
            self.message_lbl.hide()
        # Last page
        else:
            self.enable_back()
            self.disable_next()
            self.enable_finish()
            self.message_lbl.show()

    def enable_next(self):
        self.next_btn.set_sensitive(True)

    def enable_back(self):
        self.previous_btn.set_sensitive(True)

    def enable_finish(self):
        #self.finish_button.set_sensitive(True)
        self.next_btn.set_label(gtk.STOCK_APPLY)
        self.wizard_finished = True
    
    def disable_next(self):
        self.next_btn.set_sensitive(False)

    def disable_back(self):
        self.previous_btn.set_sensitive(False)

    #def disable_finish(self):
        #self.finish_button.set_sensitive(False)
        
    def disable_finish(self):
        self.next_btn.set_label(gtk.STOCK_GO_FORWARD)

    def on_next_btn__clicked(self, *args):
        assert self.current.has_next_step(), self.current
        self.change_step(self.current.next_step())
            
    def on_previous_btn__clicked(self, *args):
        self.change_step(self.current.previous_step())
 
    #def on_finish_button__clicked(self, *args):
        #self.finish()

    def on_cancel_btn__clicked(self, *args):
        self.cancel()

    def set_message(self, message):
        self.message_lbl.set_text(message)

    def cancel(self, *args):
        # Redefine this method if you want something done when cancelling the
        # wizard.
        self.retval = None
        return self.close()

    def finish(self):
        # Redefine this method if you want something done when finishing the
        # wizard.
        return self.close()
