'''
When imported all undefined names now act as strings, and operators between them are evaluated as strings.

print(john.smith@example.com) will therefore actually print 'john.smith@example.com'

Made for fun, hope no one gets hurt by the use of this.
'''

import inspect
import dis

def lop(operator):
    '''Operator decorator for left-side-centered operators (__add__, __sub__)'''
    def inner(func):
        def innest(self, other):
            return self.__class__(f'{self}{operator}{other}')
        return innest
    return inner

def rop(operator):
    '''Operator decorator for right-side-centered operators (__radd__, __rsub__)'''
    def inner(func):
        def innest(self, other):
            return self.__class__(f'{other}{operator}{self}')
        return innest
    return inner

def cop(operator):
    '''
    When Python tries to compare a Name object with a string using the <, <=, >, or >= operators,
    instead of calling something like __rlt__ it will flip the operands and call __lt__

    'a'<b might therefore be transformed into 'b>a'.
    
    In this decorator we check the bytecode for what comparsion should have been executed and if
    it does not match what we are attempting we flip the operands and use the correct operator instead.
    '''
    def inner(func):
        def innest(self, other):
            frame = inspect.currentframe().f_back
            instrs = list(dis.get_instructions(frame.f_code))

            # Every instruction is two bytes long and f_lasti is the byte index
            lasti = instrs[frame.f_lasti//2]

            # If this gets called and it was not a compare operation
            # idk wtf has happened but might happen so why not sanity check
            assert lasti.opname == 'COMPARE_OP'
            if lasti.argval == operator:
                return self.__class__(f'{self}{operator}{other}')
            else:
                return self.__class__(f'{other}{lasti.argval}{self}')
        return innest
    return inner


class Name(str):

    def __call__(self, *args, **kwargs):
        # Formatting the args and kwargs to a string
        strs = list(map(str, args)) + [f'{k}={v}' for k, v in kwargs.items()]
        return self.__class__(f'{self}({",".join(strs)})')

    def __getitem__(self, key):
        # Slicing notation gets messed up here and I tried
        # accounting for it but there were so many edge cases
        # I decided to just leave it as is, feel free to experiment
        return self.__class__(f'{self}[{key}]')

    def __invert__(self):
        return self.__class__(f'~{self}')

    @lop('+')
    def __add__(): pass
    @rop('+')
    def __radd__(): pass

    @lop('-')
    def __sub__(): pass
    @rop('-')
    def __rsub__(): pass
    
    @lop('*')
    def __mul__(): pass
    @rop('*')
    def __rmul__(): pass

    @lop('@')
    def __matmul__(): pass
    @rop('@')
    def __rmatmul__(): pass
    
    @lop('/')
    def __truediv__(): pass
    @rop('/')
    def __rtruediv__(): pass

    @lop('//')
    def __floordiv__(): pass
    @rop('//')
    def __rfloordiv__(): pass

    @lop('%')
    def __mod__(): pass
    @rop('%')
    def __rmod__(): pass

    @lop('**')
    def __pow__(): pass
    @rop('**')
    def __rpow__(): pass

    @lop('<<')
    def __lshift__(): pass
    @rop('<<')
    def __rlshift__(): pass

    @lop('>>')
    def __rshift__(): pass
    @rop('>>')
    def __rrshift__(): pass
    
    @lop('&')
    def __and__(): pass
    @rop('&')
    def __rand__(): pass
    
    @lop('|')
    def __or__(): pass
    @rop('|')
    def __ror__(): pass

    @lop('^')
    def __xor__(): pass
    @rop('^')
    def __rxor__(): pass

    @lop('==')
    def __eq__(): pass
    @rop('==')
    def __req__(): pass

    @lop('!=')
    def __ne__(): pass
    @rop('!=')
    def __rne__(): pass

    @cop('>')
    def __gt__(): pass

    @cop('<')
    def __lt__(): pass

    @cop('>=')
    def __ge__(): pass

    @cop('<=')
    def __le__(): pass

    @lop('.')
    def __getattr__(): pass

if __name__ != '__main__':
    frame = inspect.currentframe().f_back
    # Loop until we are in the actual importing module,
    # not importlib or some other internal stuff
    while frame.f_globals['__name__'] != '__main__':
        frame = frame.f_back

    def findnames(code):
        '''Find all names in a code object as well as the names of
        any code objects (functions) within them.'''
        names = code.co_names
        for const in code.co_consts:
            # Grab the code class (can you import it from somewhere?)
            if isinstance(const, type((lambda:None).__code__)):
                names += findnames(const)
        return names

    for name in findnames(frame.f_code):
        # Only overwrite names that are not already defined
        if  name not in __builtins__ and \
            name not in frame.f_globals and \
            name not in frame.f_locals:
            frame.f_globals[name] = Name(name)