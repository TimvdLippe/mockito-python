_STUBBING_ = -2

class Mock:
  def __init__(self):
    self.invocations = []
    self.stubbed_invocations = []
    self.mocking_mode = None
  
  def __getattr__(self, method_name):
    if self.mocking_mode == _STUBBING_:
      return InvocationStubber(self, method_name)

    if self.mocking_mode != None:
      return InvocationVerifier(self, method_name)
      
    return InvocationMemorizer(self, method_name)
  
  def finishStubbing(self, invocation):
    if (self.stubbed_invocations.count(invocation)):
      self.stubbed_invocations.remove(invocation)
      
    self.stubbed_invocations.append(invocation)
    self.mocking_mode = None

class ClassMock(Mock):
    def __init__(self, klass):
        self.klass = klass
        Mock.__init__(self);
        
    def __is_instance_method(self, method_name):
        try:
            return getattr(self.klass, method_name).im_self is not None
        except AttributeError:
            return False
    
    def __getattr__(self, method_name):
      if self.mocking_mode == _STUBBING_:
        inv_stubber = InvocationStubber(self, method_name)
        if self.__is_instance_method(method_name):
            method = eval("lambda cls: InvocationMemorizer(cls.mock, '#{method_name}')()");
            setattr(self.klass, "mock", self)
            setattr(self.klass, method_name, classmethod(method))
        return inv_stubber

      if self.mocking_mode != None:
        return InvocationVerifier(self, method_name)
    
      return None
    
class Invocation:
  def __init__(self, mock, method_name):
    self.method_name = method_name
    self.mock = mock
    self.answers = []
    self.verified = False
    
  def __cmp__(self, other):
    return 0 if self.matches(other) else 1
    
  def matches(self, invocation):
    if self.method_name == invocation.method_name and self.params == invocation.params:
        return True
    if len(self.params) != len(invocation.params):
        return False
    return self.__compareUsingMatchers(invocation)

  def __compareUsingMatchers(self, invocation):  
    for x, p1 in enumerate(self.params):
        p2 = invocation.params[x]
        if isinstance(p1, Matcher):
            if not p1.satisfies(p2): return False
        elif p1 != p2: return False
    return True
  
  def stubWith(self, answer, chained_mode):
    if chained_mode:
        self.answers[-1].append(answer.current())
    else:
        self.answers.append(answer)
    self.mock.finishStubbing(self)
  
class InvocationMemorizer(Invocation):
  def __call__(self, *params, **named_params):
    self.params = params
    self.mock.invocations.append(self)
    
    for invocation in self.mock.stubbed_invocations:
      if self.matches(invocation):
        return invocation.answers[0].answer()
    
    return None
  
class InvocationVerifier(Invocation):
  def __call__(self, *params, **named_params):
    self.params = params
    matches = 0
    for invocation in self.mock.invocations:
      if self.matches(invocation):
        matches += 1
        invocation.verified = True
  
    if (matches != self.mock.mocking_mode):
      raise VerificationError()

class InvocationStubber(Invocation):
  def __call__(self, *params, **named_params):
    self.params = params    
    return AnswerSelector(self)

class AnswerSelector():
  def __init__(self, invocation):
    self.invocation = invocation
    self.chained_mode = False
    
  def thenReturn(self, return_value):
    self.invocation.stubWith(Returns(return_value), self.chained_mode)
    self.chained_mode = True
    return self
    
  def thenRaise(self, exception):
    self.invocation.stubWith(Throws(exception), self.chained_mode)     
    self.chained_mode = True
    return self

_RETURNS_ = 1
_THROWS_ = 2

class Answer():
  def __init__(self, value, type):
    self.answers = [[value, type]]
    self.index = 0

  def current(self):
    return self.answers[self.index]

  def append(self, answer):
    self.answers.append(answer)

  def answer(self):      
    answer = self.current()[0] 
    type = self.current()[1]
    self.index += 1
    if self.index >= len(self.answers): self.index = len(self.answers) - 1
    if type == _THROWS_: raise answer
    return answer

class Returns(Answer):
  def __init__(self, value):
    Answer.__init__(self, value, _RETURNS_)

class Throws(Answer):
  def __init__(self, value):
    Answer.__init__(self, value, _THROWS_)
      
class VerificationError(AssertionError):
  pass
  
def verify(mock, count=1):
  mock.mocking_mode = count
  return mock

def times(count):
  return count

def when(mock):
  mock.mocking_mode = _STUBBING_  
  return mock

def verifyNoMoreInteractions(*mocks):
  for mock in mocks:
    for i in mock.invocations:
      if not i.verified:
        raise VerificationError("Unwanted interaction: " + i.method_name)
      
class Matcher:
  def satisfies(self, arg):
      pass
  
class any(Matcher):           
  def __init__(self, type=None):
      self.type = type
    
  def satisfies(self, arg):
      return isinstance(arg, self.type) if self.type else True

class contains(Matcher):
  def __init__(self, sub):
      self.sub = sub
      
  def satisfies(self, arg):
      return self.sub and len(self.sub) > 0 and arg.find(self.sub) > -1
 