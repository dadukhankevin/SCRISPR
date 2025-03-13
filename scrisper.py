import os
import random
import json
from llm_base import LLMBase
from agents import PhenotypeAgent, GenotypeAgent, TournamentAgent, MaskedCrossoverAgent, UnmaskMutationAgent, TelephoneMutationAgent, ProjectAgent, clean_code
from genetics import Individual
import uuid
from typing import Callable
import matplotlib.pyplot as plt

class Layer():
    """Base class for all layers in the genetic algorithm pipeline."""
    def __init__(self, run_function: Callable, selection_function: Callable = lambda x: x):
        self.environment: Environment = None
        self.selection_function = selection_function
        self.run_function = run_function
    def execute(self, individuals: list[Individual]):
        individuals = self.selection_function(individuals)
        self.run_function(individuals)
    def setup(self, environment: "Environment"):
        """
        Initialize the layer with a reference to the environment.
        
        Args:
            environment: The Environment instance this layer belongs to
        """
        self.environment = environment

        
class Environment:
    def __init__(self, project_agent: ProjectAgent, layers: list[Layer]):
        self.project_agent = project_agent
        self.layers = layers
        self.individuals = []
        self.schematic = None
        self.fitness_code = None
        self.project_prompt = None
        self.history = []

    def init_project(self, prompt):
        self.project_prompt = prompt
        raw_response, schematic, fitness = self.project_agent.generate_project_codes(prompt)
        schematic, fitness = clean_code(schematic), clean_code(fitness)

        # Get absolute path for prompts directory
        current_dir = os.getcwd()
        prompts_path = os.path.join(current_dir, "prompts", "universal_code_injections", "partial_fitness.partial_py")
        
        with open(prompts_path, "r", encoding="utf-8") as f:
            universal_fitness_code = f.read()
            
        completed_fitness_code = universal_fitness_code.replace("{generated_fitness_code}", fitness)

        # Create environment directories with absolute paths
        env_dir = os.path.join(current_dir, "environment")
        individuals_dir = os.path.join(env_dir, "individuals")
        dead_individuals_dir = os.path.join(env_dir, "dead_individuals")
        
        os.makedirs(env_dir, exist_ok=True)
        os.makedirs(individuals_dir, exist_ok=True)
        os.makedirs(dead_individuals_dir, exist_ok=True)

        # Save files with absolute paths
        schematic_path = os.path.join(env_dir, "schematic.md")
        fitness_path = os.path.join(env_dir, "fitness.py")
        
        with open(schematic_path, "w", encoding="utf-8") as f:
            f.write(schematic)
        with open(fitness_path, "w", encoding="utf-8") as f:
            f.write(completed_fitness_code)

        self.schematic = schematic
        self.fitness_code = fitness
        return raw_response, schematic, fitness
    def compile(self):
        for layer in self.layers:
            layer.setup(self)
    def get_latest_individual(self):
        return self.individuals[-1].directory
    
    def evolve(self, generations: int):
        for _ in range(generations):
            for layer in self.layers:
                layer.run(self.individuals)
            self.history.append(self.individuals[-1].fitness)
            # save to history.png with improved formatting
            plt.figure(figsize=(10, 6))
            plt.plot(self.history, 'b-', linewidth=2)
            plt.title('Fitness History Over Generations')
            plt.xlabel('Generation')
            plt.ylabel('Fitness Score')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig("history.png", dpi=300)
            plt.close()
    
    def create_individual(self, phenotype: str, genotype: str, requirements: str):
        ind_id = str(uuid.uuid4())
        
        # Create directory for the individual using absolute path
        ind_dir = os.path.abspath(os.path.join("environment", "individuals", ind_id))
        os.makedirs(ind_dir, exist_ok=False)
        
        # Save all artifacts using absolute paths
        with open(os.path.join(ind_dir, "prompt.md"), "w", encoding="utf-8") as f:
            f.write(phenotype)
        
        with open(os.path.join(ind_dir, "genotype.py"), "w", encoding="utf-8") as f:
            f.write(genotype)
            
        with open(os.path.join(ind_dir, "requirements.txt"), "w", encoding="utf-8") as f:
            f.write("pytest\n"+requirements)
            
        with open(os.path.join(ind_dir, "data.json"), "w", encoding="utf-8") as f:
            json.dump(data_json_default, f)
            
        # Create and add the individual to the population
        individual = Individual(
            directory=ind_dir,  # Using absolute path
            fitness=0,
            idstr=ind_id
        )
        success = individual.setup()
        
        
        if success:
            self.individuals.append(individual)



data_json_default = {
    "score": 0,
    "iteration": 0,
    "runtimes": [],
    "parent_ids": [],
}

class Populate(Layer):
    def __init__(self, phenotype_agent: PhenotypeAgent, genotype_agent: GenotypeAgent, population_size: int):
        super().__init__(self.run)
        self.phenotype_agent = phenotype_agent
        self.genotype_agent = genotype_agent
        self.population_size = population_size

    def run(self, individuals: list[Individual]):
        """
        Create individuals up to the specified population size.
        
        Args:
            population_size: The target number of individuals to create
        """
        while len(self.environment.individuals) < self.population_size:
            
            # Generate phenotype (prompt) from project description
            phenotype_response, phenotype = self.phenotype_agent.generate_phenotype(
                self.environment.project_prompt,
                temperature=0.7
            )
            
            # Generate genotype (implementation) from phenotype
            genotype_response, genotype_code, requirements = self.genotype_agent.generate_genotype(
                f"Implement the following:\n\n{phenotype}\n\nSchematic:\n{self.environment.schematic}",
                temperature=0
            )
            
            self.environment.create_individual(phenotype, genotype_code, requirements)

class MaskedCrossover(Layer):
    def __init__(self, crossover_agent: MaskedCrossoverAgent, selection_function: Callable, num_families: int, num_children: int, genotype_agent: GenotypeAgent):
        super().__init__(self.run)
        self.crossover_agent = crossover_agent
        self.selection_function = selection_function
        self.genotype_agent = genotype_agent
        self.num_families = num_families
        self.num_children = num_children

    def run(self, individuals: list[Individual]):
        parent1, parent2 = self.selection_function(individuals)

        for _ in range(self.num_families):
            for _ in range(self.num_children):
                response, child_prompt = self.crossover_agent.crossover(parent1, parent2)

                genotype_response, genotype_code, requirements = self.genotype_agent.generate_genotype(
                f"Implement the following:\n\n{child_prompt}\n\nSchematic:\n{self.environment.schematic}",
                temperature=0)
                self.environment.create_individual(child_prompt, genotype_code, requirements)

class MaskedMutation(Layer):
    def __init__(self, mutation_agent: UnmaskMutationAgent, selection_function: Callable, genotype_agent: GenotypeAgent, mask_rate: float = 0.3, mask_size: range = range(1, 10)):
        super().__init__(self.run)
        self.mutation_agent = mutation_agent
        self.selection_function = selection_function
        self.genotype_agent = genotype_agent
        self.mask_rate = mask_rate
        self.mask_size = mask_size

    def run(self, individuals: list[Individual]):
        
        for individual in individuals:
            # Apply masked mutation to the prompt
            response, mutated_prompt = self.mutation_agent.unmask_mutation(
                individual.get_prompt(), 
                temperature=0.7, 
                mask_rate=self.mask_rate, 
                mask_size=self.mask_size, 
                split_by_spaces=True
            )
            
            # Generate genotype from the mutated prompt
            genotype_response, genotype_code, requirements = self.genotype_agent.answer(
                f"Implement the following:\n\n{mutated_prompt}\n\nSchematic:\n{self.environment.schematic}",
                self.genotype_agent.model,
                tags=["genotype_py", "requirements_txt"]
            )
            individual.reset_attributes(mutated_prompt, genotype_code, requirements)
        
class SortByFitness(Layer):
    def __init__(self):
        super().__init__(self.run)

    def run(self, individuals: list[Individual]):
        # Sort individuals by fitness in descending order (highest fitness first)
        self.environment.individuals.sort(key=lambda x: x.fitness, reverse=True)
        return self.environment.individuals

class CapPopulation(Layer):
    def __init__(self, max_size: int):
        super().__init__(self.run)
        self.max_size = max_size

    def run(self, individuals: list[Individual]):
        # Make sure individuals are sorted by fitness before capping
        if not individuals:
            return []
            
        # Kill individuals that exceed the maximum population size
        excess_individuals = self.environment.individuals[self.max_size:]
        for individual in excess_individuals:
            # Call kill() to move the individual to dead_individuals directory
            individual.kill()
            
        # Update the environment's individuals list to only include the survivors
        self.environment.individuals = self.environment.individuals[:self.max_size]
        return self.environment.individuals