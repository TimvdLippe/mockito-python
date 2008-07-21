_STUBBING_=-2

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
  
class Invocation:
  def __init__(self, mock, method_name):
    self.method_name = method_name
    self.mock = mock
    self.answers = []
    self.verified = False
    
  def __cmp__(self, other):
    if self.matches(other):
      return 0
    else:
      return 1
    
  def matches(self, invocation):
    if self.method_name == invocation.method_name and self.params == invocation.params:
        return True
    if len(self.params) != len(invocation.params):
        return False
    return self.__compareUsingMatchers(invocation)

  def __compareUsingMatchers(self, invocation):  
    for x, p1 in enumerate(self.params):
        p2 = invocation.params[x]
        if isinstance(p1, Any):
            if not p1.satisfiedBy(p2):
                return False
        elif p1 != p2:
            return False
    return True
  
  def stubWith(self, answer):
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
        matches+=1
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
    
  def thenReturn(self, return_value):
    self.invocation.stubWith(Returns(return_value))
    
  def thenRaise(self, exception):
    self.invocation.stubWith(Throws(exception))     

class Returns():
  def __init__(self, return_value):
    self.return_value = return_value
  
  def answer(self):
    return self.return_value

class Throws():
  def __init__(self, exception):
    self.exception = exception
  
  def answer(self):
    raise self.exception
      
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
      
class Any:
    def satisfiedBy(self, arg):
        return True

class AnyInt(Any):
    def satisfiedBy(self, arg):
        return isinstance(arg, int)

class AnyStr(Any):
    def satisfiedBy(self, arg):
        return isinstance(arg, str)

class AnyFloat(Any):
    def satisfiedBy(self, arg):
        return isinstance(arg, float)

any = Any()
anyInt = AnyInt()
anyStr = AnyStr()
anyFloat = AnyFloat()
