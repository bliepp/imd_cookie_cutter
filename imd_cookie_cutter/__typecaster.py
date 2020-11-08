#!/usrb/bin/python3
#
#
#


def boolify(s):
    if s == 'True' or s == 'true':
            return True
    if s == 'False' or s == 'false':
            return False
    raise ValueError('Not Boolean Value!')


def estimate_type(var):
    '''estimate_ts the str representation of the variables type'''
    var = str(var) #important if the parameters aren't strings...
    for caster in (boolify, int, float):
            try:
                    return caster(var)
            except ValueError:
                    pass
    return var
