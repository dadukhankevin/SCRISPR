# SCRISPER V0

SCRISPER (Software Creation via Random Improvement and Selection of Prompts for Evolution and Refinement) is a system designed to evolve software solutions by combining genetic algorithms with large language models (LLMs). It iteratively refines textual prompts to generate increasingly effective software implementations.

Note: super early stage, not at all fully tested or proven!

## Overview

SCRISPER leverages evolutionary principles—such as mutation, crossover, and selection—to iteratively improve software solutions. Instead of directly evolving code, SCRISPER evolves the prompts that instruct LLMs to generate code. This approach allows the system to explore a wide range of conceptual solutions, potentially uncovering novel and effective approaches to complex programming challenges.

## How SCRISPER Works

The SCRISPER workflow consists of the following steps:

1. **Problem Definition**: Provide a clear textual description of the programming challenge you want to solve.
2. **Fitness Evaluation**: SCRISPER generates a comprehensive test suite and fitness function to objectively evaluate the quality of generated solutions.
3. **Population Initialization**: The system creates an initial population of "individuals," each consisting of a unique prompt and its corresponding generated code implementation.
4. **Evolutionary Process**: Through iterative cycles of mutation, crossover, and selection, SCRISPER refines the prompts, progressively improving the generated software solutions.
5. **Final Output**: After multiple generations, SCRISPER outputs optimized, tested, and functional software solutions addressing the original problem.

## Key Concepts

### Genotype and Phenotype

SCRISPER distinguishes between two core concepts:

- **Genotype**: The textual prompt describing the software solution.
- **Phenotype**: The actual software implementation generated from the genotype.

This separation allows evolution to occur at the conceptual level, enabling the exploration of diverse and innovative solutions.

### Genetic Operations

SCRISPER employs several specialized novel genetic operations tailored for prompt-based evolution:

- **Telephone Mutation**: Generates software from a prompt, then creates a new prompt by describing the generated software, allowing implementation details to influence future generations.
- **Masked Mutation**: Randomly masks portions of a prompt and uses an LLM to fill in the gaps, introducing controlled variation.
- **Smart Crossover**: Combines two parent prompts intelligently using an LLM, merging beneficial features from both.
- **Masked Smart Crossover**: Masks parts of parent prompts before recombination, encouraging novel and unexpected prompt combinations.

### Selection Methods

SCRISPER uses advanced selection methods to maintain both quality and diversity:

- **Ranked Levenshtein Selection**: Selects individuals based on fitness and textual diversity, promoting varied yet effective solutions.
- **Smart Tournament Selection**: Uses an LLM to evaluate and select the best individuals from randomly chosen subsets, enabling nuanced assessments beyond numeric fitness scores.

## System Architecture

SCRISPER employs an agent-based architecture, with specialized agents handling distinct aspects of the evolutionary process:

- **Project Agent**: Initializes projects and generates fitness functions.
- **Phenotype Agent**: Creates implementation prompts from problem descriptions.
- **Genotype Agent**: Generates code implementations from prompts.
- **Mutation and Crossover Agents**: Facilitate genetic operations.
- **Tournament Agent**: Conducts selection processes.

## Examples

SCRISPER is meant speficically for creating small scripts where innovation is the main goal. Eg. Its better at generating new activation functions, and isn't what you'd use for a web app (yet!).

Here's an example:
```python
from scrisper import general_scrisper
from scrisper.llm_base import LLMBase

# Example usage
llm = LLMBase(base_url="https://api.example.com", api_key="your_api_key") # try to use groq!
general_scrisper("Create a function that adds two numbers", llm=llm, model="qwen-2.5-coder-32b", generations=3)
```
If you want to more customizable controls SCRISPER is built like Finch and Keras as it is made of layers, you can view the example in examples/layered_example.py

## Getting Started

To set up and run SCRISPER:

1. Clone the repository.
2. Install dependencies listed in requirements.txt.
3. Define your problem prompt clearly.
4. Run the evolutionary algorithm (algorithm.py) to initiate the process.

## Contributing

Contributions are welcome. Please open an issue or submit a pull request with your proposed changes or improvements.

## License

MIT License, have fun.