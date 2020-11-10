import json

class Recipe():
    def __init__(self, name, q, T, inputs):
        """
        name is the name of the recipe e.g. circuit, 4pcb
        q is the number produced per recipe
        T is the time it takes to make the recipe
        inputs is a list of inputs of the form {name: q}
        where name is the name of the input and q is the number
        required per recipe
        """
        self.q = q
        self.T = T
        self.inputs = inputs

        self.extra = 0 #The number of excess products per second to produce
        #This is the base frequency of each input
        self.Fib = {name: N/q*1.25/T for k:N in inputs}

    def get_inputs(self, Fo, Np, Ns):
        """
        For a given desired output frequency, 
        number of productivity modules,
        number of speed modules,
        return the input frequencies of each input as
        {name: rate}
        """
        out_rates = {
            name: Fi*(1+.1*Np)*(1+.5*Ns-.15*Np)
            for Fi in name:self.Fib
            }

        return out_rates


class Factory():
    def __init__(self, filename):
        raw = json.load(open(filename, 'r'))

