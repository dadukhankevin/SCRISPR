import sys
import os
# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrisper import Environment, Populate, MaskedCrossover, MaskedMutation, SortByFitness, CapPopulation
from genetics import Individual
from agents import ProjectAgent, PhenotypeAgent, GenotypeAgent, MaskedCrossoverAgent, UnmaskMutationAgent
from llm_base import LLMBase
import random
backend_api = "https://api.groq.com/openai/v1"
model = "qwen-2.5-coder-32b"
llm = LLMBase(base_url=backend_api, api_key="")
project_agent = ProjectAgent(llm, model)
phenotype_agent = PhenotypeAgent(llm, model)
genotype_agent = GenotypeAgent(llm, model)
masked_crossover_agent = MaskedCrossoverAgent(llm, model)
unmask_mutation_agent = UnmaskMutationAgent(llm, model)

def random_parent_selection(individuals: list[Individual]):
    return random.choices(individuals, k=2)

environment = Environment(project_agent, [
    Populate(phenotype_agent, genotype_agent, population_size=2),
    MaskedCrossover(masked_crossover_agent, selection_function=random_parent_selection, num_families=2, num_children=2, genotype_agent=genotype_agent),
    MaskedMutation(unmask_mutation_agent, selection_function=random_parent_selection, genotype_agent=genotype_agent),
    CapPopulation(10)
])

environment.compile()
environment.init_project("Create a function that adds two numbers")
environment.evolve(1)








