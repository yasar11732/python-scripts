import profile
from os import makedirs
from os.path import join, dirname, isdir, isfile
import hashlib

def serialize_l_system(string, rules):
    items = [(k,v) for k,v in rules.items()]
    items.sort(key=lambda k:k[0])
    return string + ";" + ";".join("{}:{}".format(k,v) for k,v in items)

def expand_string(string, rules):
    return "".join(rules[x] for x in string)

def cached_expand_string(string, rules):

    # don't cache minimal strings to decrase I/O time
    if not len(string) > 1000:
        return expand_string(string, rules)

    cachedir = join(dirname(__file__),"lsd-cache")

    if not isdir(cachedir):
        makedirs(cachedir)

    m = hashlib.sha256()

    serialized_system = serialize_l_system(string, rules)
    m.update(serialized_system.encode('utf-8'))
    cachefile = join(cachedir, m.hexdigest())

    if isfile(cachefile):
        with open(cachefile) as f:
            return f.read()
    else:
        value = expand_string(string, rules)
        with open(cachefile, "w") as f:
            f.write(value)
        return value

string = "F"
rules = {'F':'1FF-[3-F+F+F]+[2+F-F-F]','1':'1','2':'2', '3':'3', '[':'[',']':']','-':'-','+':'+'}

def iterations(function, num_iter, string, rules):
    print("iterations:",num_iter)
    print("function", function)
    for _ in range(num_iter):
        string = function(string, rules)

profile.run('iterations(expand_string, 6, string, rules)')
profile.run('iterations(cached_expand_string, 6, string, rules)')
    
