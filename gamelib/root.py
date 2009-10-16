
class Root(object):
    
    def __init__(self):
        self.states = {}
        self.current_state = None
        
    def start(self, state_class):
        state = self.current_state
        self.states[state_class] = state_class(self)
        self.current_state = self.states[state_class]
        self.current_state.__last_state = state

    def resume(self, state_class):
        if state_class not in self.states:
            print "Error: State has not been initialized, and therefore can't be resumed."
            return
        self.current_state = self.states[state_class]
        
    def go_back(self):
        self.current_state = self.current_state.__last_state
        
    def update(self, surface):
        if self.current_state:
            self.current_state.update(surface)
        
