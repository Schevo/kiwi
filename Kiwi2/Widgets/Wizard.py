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
    gladefile = 'Wizard'
    widgets = ['message',
               'header',
               'top_separator',
               'cancel_button',
               #'finish_button',
               'back_button',
               'next_button']
    retval = None
    def __init__(self, title, first_step, size=None):
        #_AbstractDialog.__init__(self, delete_handler=self.cancel)
        Delegate.__init__(self, gladefile=self.gladefile, delete_handler=quit_if_last,
                          widgets=self.widgets)
        self.set_title(title)
        self.first_step = first_step
        if size:
            self.get_toplevel().set_default_size(size[0], size[1])
        self.change_step(first_step)

    def change_step(self, step):
        if step is None:
            # Sometimes for different reasons the wizard needs to be
            # interrupted. In this case, next/previous_step should return
            # None to get the wizard interrupted. self.cancel is called
            # because it is the most secure action to do, since interrupt
            # here does not mean success
            return self.cancel()
        self.attach_slave("wizard_slave", step)
        self.current = step
        if step.header:
            self.header.show()
            #self.top_separator.show()
            self.header.set_text(step.header)
        else:
            self.header.hide()
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
            self.message.hide()
        # Middle page
        elif self.current.has_next_step(): 
            self.enable_back()
            self.enable_next()
            self.disable_finish()
            self.message.hide()
        # Last page
        else:
            self.enable_back()
            self.disable_next()
            self.enable_finish()
            self.message.show()

    def enable_next(self):
        self.next_button.set_sensitive(True)

    def enable_back(self):
        self.back_button.set_sensitive(True)

    def enable_finish(self):
        #self.finish_button.set_sensitive(True)
        self.next_button.set_label("Finish")
        self.wizard_finished = True
    
    def disable_next(self):
        self.next_button.set_sensitive(False)

    def disable_back(self):
        self.back_button.set_sensitive(False)

    #def disable_finish(self):
        #self.finish_button.set_sensitive(False)
        
    def disable_finish(self):
        self.next_button.set_label("Next >")

    def on_next_button__clicked(self, *args):
        assert self.current.has_next_step(), self.current
        self.change_step(self.current.next_step())
            
    def on_back_button__clicked(self, *args):
        self.change_step(self.current.previous_step())
 
    #def on_finish_button__clicked(self, *args):
        #self.finish()

    def on_cancel_button__clicked(self, *args):
        self.cancel()

    def set_message(self, message):
        self.message.set_text(message)

    def cancel(self, *args):
        # Redefine this method if you want something done when cancelling the
        # wizard.
        self.retval = None
        return self.close()

    def finish(self):
        # Redefine this method if you want something done when finishing the
        # wizard.
        return self.close()
