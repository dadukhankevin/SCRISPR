import sys
import os
# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrisper import Environment, Populate, MaskedCrossover, MaskedMutation, SortByFitness, CapPopulation
from genetics import Individual
from agents import ProjectAgent, PhenotypeAgent, GenotypeAgent, MaskedCrossoverAgent, UnmaskMutationAgent
from llm_base import LLMBase
import random




def general_scrisper(project_prompt: str, llm: LLMBase, model: str, scale: float = 1, generations: int = 1):
    if scale > 1:
        print("Scaling up past 1 drastically increases token use and time. Be careful!")
    project_agent = ProjectAgent(llm, model)
    phenotype_agent = PhenotypeAgent(llm, model)
    genotype_agent = GenotypeAgent(llm, model)
    masked_crossover_agent = MaskedCrossoverAgent(llm, model)
    unmask_mutation_agent = UnmaskMutationAgent(llm, model)
    environment = Environment(project_agent, [
        Populate(phenotype_agent, genotype_agent, population_size=2 * scale),
        MaskedCrossover(masked_crossover_agent, selection_function=lambda x: random.choices(x, k=2 * scale), num_families=2 * scale, num_children=2 * scale, genotype_agent=genotype_agent),
        MaskedMutation(unmask_mutation_agent, selection_function=lambda x: random.choices(x, k=3 * scale), genotype_agent=genotype_agent),
        CapPopulation(15 * scale)
    ])

    environment.compile()
    environment.init_project(project_prompt)
    environment.evolve(generations)








