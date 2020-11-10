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

        self.Fb = 1.25*q/T #The base frequency per machine

        self.extra = 0 #The number of excess products per second to produce
#        self.Fib = {name: N/q*1.25/T for name,N in inputs.items()}
        #This is the base number of each input required per output
        self.Nib = {name: N/q for name,N in inputs.items()}

    def get_inputs(self, Fo, Np, Ns):
        """
        For a given desired output frequency, 
        number of productivity modules,
        number of speed modules,
        return the input frequencies of each input as
        {name: rate}
        """
        out_rates = {
            name: Fo*Ni/(1+.1*Np)
            for name, Ni in self.Nib.items()
            }

        return out_rates

    def get_assemblers(self, Fo, Np, Ns):
        Feff = self.Fb*(1+.5*Ns-.15*Np)*(1+.1*Np)
        N = Fo/Feff
        return N

class Factory():
    def __init__(self, filename):
        raw = json.load(open(filename, 'r'))
        self.recipes = {}
        for name, data in raw['recipes'].items() :
            self.recipes[name] = Recipe(name, **data)
        self.modules = raw['modules']

    def print(self):
        for name, rec in self.recipes.items():
            _mods = self.modules[name]
            mods = {'Np': _mods[0], 'Ns': _mods[1]}
            Fo = 45

            print(f'Recipe {name} at {Fo}/s with Np = {mods["Np"]} and Ns = {mods["Ns"]}')
            N = rec.get_assemblers(Fo, **mods)

            print(f'Requires {N:.2f} assemblers to produce')

            in_rates = rec.get_inputs(Fo, **mods)

            for in_name, rate in in_rates.items():
                print(f'  {in_name}: {rate}/s')



