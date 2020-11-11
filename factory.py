import json

class Recipe():
    def __init__(self, name, q, T, inputs, crafting_speed = 1.25):
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

        self.Fb = crafting_speed*q/T #The base frequency per machine

        self.extra = 0 #The number of excess products per second to produce
#        self.Fib = {name: N/q*1.25/T for name,N in inputs.items()}
        #This is the base number of each input required per output
        self.Nib = {name: N/q for name,N in inputs.items()}

    def get_input(self, name, Fo, Np, Ns):
        """
        For a given desired output frequency, 
        number of productivity modules,
        number of speed modules,
        return the input frequencies of each input as
        {name: rate}
        """
        return Fo*self.Nib[name]/(1+.1*Np)


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

    def get_sinks(self):
        return self.inputs.keys()

class Factory():
    def __init__(self, filename):
        raw = json.load(open(filename, 'r'))
        self.recipes = {}
        for name, data in raw['recipes'].items() :
            self.recipes[name] = Recipe(name, **data)
        self.modules = {}
        for name, (Np, Ns) in raw['modules'].items():
            self.modules[name] = {'Np': Np, 'Ns': Ns}
        self.goals = raw['goals']

        self.update_requirements()

    def update_requirements(self):
        sinks = {}
        for name in self.recipes.keys():
            sinks[name] = []
            for other in self.recipes.keys():
                if other != name and name in self.recipes[other].inputs.keys():
                    sinks[name].append(other)


        done = []
        names = self.recipes.keys()
        todo = [x for x in names if not x in done]
        self.requirements = requirements = dict(self.goals)
        while len(done) < len(names):
            for name in todo:
                if all([sink in done for sink in sinks[name]]):
                    if not name in requirements.keys(): 
                        requirements[name]=0
                    for sink in sinks[name]:
                        Fs = requirements[sink]
                        sink_recipe = self.recipes[sink]
                        mods = self.modules[sink]
                        requirements[name] += sink_recipe.get_input(name, Fs, **mods)
                    done.append(name)
                    todo.remove(name)


    def print(self):
        #raw ingredients
        requirements = self.requirements
        for name, Fo in requirements.items():
            if len(self.recipes[name].inputs.keys()) == 0:
                rate = requirements[name]
                print(f'Raw material {name} is required at a rate of {rate:.2f}/s')

        table = [["Recipe", "Rate (/s)", "# Assemblers", "Prod", "Speed"]]

        print('')
        #machine items
        for name, Fo in requirements.items():
            if len(self.recipes[name].inputs.keys()) == 0:
                continue
 
            mods = self.modules[name]
            rec = self.recipes[name]
#            print(f'Recipe {name} at {Fo:.2f}/s with Np = {mods["Np"]} and Ns = {mods["Ns"]}')
            N = rec.get_assemblers(Fo, **mods)

#            print(f'Requires {N:.2f} assemblers to produce')

            in_rates = rec.get_inputs(Fo, **mods)
#            for in_name, rate in in_rates.items():
#                print(f'  {in_name}: {rate:.2f}/s')
            list_name = name
            if name in self.goals.keys():
                list_name += '*'
            table.append([list_name, Fo, N, mods['Np'], mods['Ns']])

        import tabulate
        print(tabulate.tabulate(table, headers='firstrow'))

        print('')
        #inputs required for circuit
        target = "circuit"
        Fo = requirements[target]
        mods = self.modules[target]
        assemblers = self.recipes[target].get_assemblers(Fo, **mods)
        print(f'Producing {target} at {Fo:.2f}/s from {assemblers} machines')
        for name, rate in self.recipes[target].get_inputs(Fo, **mods).items():
            inmods = self.modules[name]
            assemblers = self.recipes[name].get_assemblers(rate, **inmods)
            print(f' * Requires {name} at {rate:.2f}/s from {assemblers} machines')


