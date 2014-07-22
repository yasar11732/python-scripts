
class CompressedLString(object):
    """This class implements a modified version of lzw algorithm,
    in order to decrease time and space complexity of L-String growth process.

    At least, I think it would solve huge space complexity when iterations are too high

    Space complexity also contributes to time complexity, because it causes big loops
	
	Note to self: This doesn't work as intended. Constantly compressing is too expensive
	that it doesn't worth it. Find an alternative solution.
    """

    def __init__(self, axiom, rules):

        self.terminals=[] # list of characters
        self.symbols  =[] # list of tuples
        self.rules = {}

        self.compression_index=0

        self.iterations = 0

        "Initiate symbols"
        for x in axiom:
            self.append_terminal(x)
            self.append_symbol((self.terminals.index(x),))

        for x in rules.keys():
            self.append_terminal(x)
            self.append_symbol((self.terminals.index(x),))
    
        for x in rules.values():
            for k in x:
                # print(k)
                self.append_terminal(k)
                self.append_symbol((self.terminals.index(k),))

        "Rewrite rules with new symbol values"
        for k,v in rules.items():
            key = self.terminals.index(k)
            value = []
            for t in v:
                value.append(self.terminals.index(t))
            self.rules[key] = tuple(value)

        self.string = [self.terminals.index(x) for x in axiom]

    def append_symbol(self, s):
        if s not in self.symbols:
            self.symbols.append(s)

    def append_terminal(self,t):
        if t not in self.terminals:
            self.terminals.append(t)

    def grow(self):
        new_string=[]
        for x in self.string:
            new_string.extend(self.get_rule(x))
        self.string=new_string

    def get_rule(self,x):
        try:
            return self.rules[x]
        except KeyError:
            return (x,)

    def uncompress(self, string=None):

        if not string:
            string=self.string
        
        for x in string:
            value = self.symbols[x]
            if len(value) == 1 and value[0] == x:
                yield self.terminals[x]
            else:
                yield from self.uncompress(value)
            

            

    def append_symbol_and_rule(self, symbol):
        if symbol in self.symbols:
            return

        self.symbols.append(symbol)

        rule = []

        for x in symbol:
            rule.extend(self.get_rule(x))

        self.rules[self.symbols.index(symbol)] = tuple(rule)

    def iterate(self, times=1):
        for _ in range(times):
            self.grow()

    
    def compress(self):

        begin_index=0
        end_index=1
        strlen=len(self.string)
        output=[]
        prev_slice = None
        
        while True:
            "Find the longest match in dictionary"
            current_slice = tuple(self.string[begin_index:end_index])
            while current_slice in self.symbols:
                end_index+=1
                current_slice = tuple(self.string[begin_index:end_index])
                if not end_index < strlen:  ## end of string
                    break

            if current_slice in self.symbols:  # we matched a symbol until the end of stream
                output.append(self.symbols.index(current_slice))
                break

            x = self.symbols.index(current_slice[:-1])

            self.append_symbol((x,))
            output.append(x)
            self.append_symbol_and_rule(current_slice)

            begin_index=end_index-1

        self.string=output

if __name__ == "__main__":
    a = CompressedLString("F",{"F":"F+F-F-F+F"})
        
        
            
    
