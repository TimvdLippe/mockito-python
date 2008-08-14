class StaticMocker():
  """Deals with both static AND class methods"""
  
  def __init__(self):
    self.stubbed_statics = []
    self.static_mocks = {}
    
  def stub(self, invocation):
    self.static_mocks[invocation.getMockedObj()] = invocation.mock
    def new_static_method(*params, **named_params): 
      i = invocation.mock.__getattr__(invocation.method_name)
      return i.__call__(*params, **named_params)
      
    s = (invocation.getMockedObj(), getattr(invocation.getMockedObj(), invocation.method_name))
    self.stubbed_statics.append(s)
    setattr(invocation.getMockedObj(), invocation.method_name, staticmethod(new_static_method))