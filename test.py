try:
    print(john.smith+py@example.com)
except NameError as err:
    print(err)
# -> name 'john' is not defined

import quotelessstrings

# But now you can finally write email addreses
# without any unnecessary surrounding quotes!
print(john.smith+py@example.com)
# -> john.smith+py@example.com

# Basically all operators work except ones you can't overwrite
# such as in, is, and, or etc.
print((a^b)**c+d&e>=f()%g|h<<i>>j)

# Overall it's all sorts of cursed and should never be used ok bye