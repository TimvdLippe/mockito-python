from test_base import *
from mockito import *

class MockitoVerificationErrorsTest(TestBase):
    
  def testVerificationErrorPrintsNicely(self):
    mock = Mock()
    try:
      verify(mock).foo()
    except VerificationError, e:
      self.assertEquals("\nWanted but not invoked: foo()", e.message)
      
  def testVerificationErrorPrintsNicelyArguments(self):
    mock = Mock()
    try:
      verify(mock).foo(1, 2)
    except VerificationError, e:
      pass
    self.assertEquals("\nWanted but not invoked: foo(1, 2)", e.message)
    
  def testVerificationErrorPrintsNicelyStringArguments(self):
    mock = Mock()
    try:
      verify(mock).foo(1, 'foo')
    except VerificationError, e:
      pass
    self.assertEquals("\nWanted but not invoked: foo(1, 'foo')", e.message)         

if __name__ == '__main__':
  unittest.main()