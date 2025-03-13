import os
import random
import json
from llm_base import LLMBase


PROJECT_PROMPT = open("prompts/project_agent.md").read()
TOURN_PROMPT = open("prompts/tournament.md").read()
TELE_PROMPT = open("prompts/telephone_agent.md").read()
UNMASK_CROSSOVER_PROMPT = open("prompts/unmask_crossover.md").read()
UNMASK_MUTATION_PROMPT = open("prompts/unmask_mutation.md").read()
PHENOTYPE_PROMPT = open("prompts/phenotype_agent.md").read()
GENOTYPE_PROMPT = open("prompts/genotype_agent.md").read()
def parse_xml_tag(tag, text):
    start = text.find(f"<{tag}>")
    if start == -1:
        raise ValueError(f"Opening tag <{tag}> not found in text")
    
    start_content = start + len(f"<{tag}>")
    end = text.find(f"</{tag}>", start_content)
    if end == -1:
        # If closing tag not found, return everything after the opening tag
        content = text[start_content:]
        print(f"No closing tag found for <{tag}>. Using content: {content}")
        return content
    
    content = text[start_content:end]
    
    return content
def clean_code(code):
    return code.replace("```python", "").replace("```", "")

class Agent:
    def __init__(self, llm: LLMBase, system_prompt: str):
        """
        Initialize an agent with an LLM backend and system prompt.
        
        Args:
            llm: LLMBase instance for generating completions
            system_prompt: The system prompt that defines the agent's behavior
        """
        self.llm = llm
        self.system_prompt = system_prompt
        self.messages = [{'role': 'system', 'content': self.system_prompt}]

    def answer(self, prompt: str, model: str, temperature: float = .7, max_tokens: int = 32000,  tags: list[str] = None) -> tuple[str, list[str]]:
        """
        Send a prompt to the LLM and get a response.
        
        Args:
            prompt: The user prompt to send to the LLM
            model: Optional override for the default model
            temperature: Optional override for the default temperature
            max_tokens: Optional override for the default max_tokens
            
        Returns:
            The text response from the model
        """
        self.messages.append({'role': 'user', 'content': prompt})
        response = self.llm.chat_completion(
            messages=self.messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        self.messages.append({'role': 'assistant', 'content': response})
        parsed_tags = []
        if tags:            
            for tag in tags:
                parsed_tags.append(parse_xml_tag(tag, response))
        return response, parsed_tags



class ProjectAgent(Agent):
    def __init__(self, llm: LLMBase, model: str = "gemma3-27b"):
        super().__init__(llm, PROJECT_PROMPT)
        self.model = model


    def generate_project_codes(self, prompt):
       raw_response, [schematic, fitness] = super().answer(prompt, self.model,temperature=.7, tags=["schematic", "fitness"])
       return raw_response, schematic, fitness

    
    
class TournamentAgent(Agent):
    def __init__(self, llm: LLMBase, model: str = "gemma3-27b"):
        super().__init__(llm, TOURN_PROMPT)
        self.model = model

    def mutate(self, evolved_prompts, problem_prompt, temperature: float = 0):
        message = f"Here are some prompts to solve the problem, '{problem_prompt}':\n"
        for i, prompt in enumerate(evolved_prompts):
            message += f"<example name=\"example_{i}\">\n{prompt}\n</example>\n"
        message += f"\nHere is the problem prompt:\n{problem_prompt}"
        response, [selection] = super().answer(message, self.model, temperature=temperature, tags=["<selection>"])
        return response, selection

class TelephoneMutationAgent(Agent):
    def __init__(self, llm: LLMBase, model: str = "gemma3-27b"):
        super().__init__(llm, TELE_PROMPT)
        self.model = model

    def telephone_mutation(self, code, temperature: float = 0): # here temperature can be seen as mutation rate or something.
        """
        Analyzes the provided code and generates a prompt that could produce this code.
        
        Args:
            code: The code to analyze
            temperature: The temperature to use for generation
            
        Returns:
            A tuple containing (raw_response, generated_prompt)
        """
        message = f"Here is some code to write a prompt for:\n```\n{code}\n```"
        response, [prompt] = self.answer(message, self.model, temperature=temperature, tags=["prompt"])
        return response, prompt
    
class UnmaskMutationAgent(Agent):
    def __init__(self, llm: LLMBase, model: str = "gemma3-27b"):
        super().__init__(llm, UNMASK_MUTATION_PROMPT)
        self.model = model

    def unmask_mutation(self, prompt, temperature: float = 0, mask_rate: float = 0.5, mask_size: range = range(1, 10), split_by_spaces: bool = False):
        """
        Fills in masked sections of a prompt with enhanced content.
        
        Args:
            prompt: The prompt to apply masking to
            temperature: The temperature to use for generation
            mask_rate: The probability of masking a section of text
            mask_size: The range of token sizes to mask
            split_by_spaces: If True, splits text by spaces before masking, otherwise masks by characters
            
        Returns:
            A tuple containing (raw_response, unmasked_prompt)
        """
        # Apply masking to the prompt
        if split_by_spaces:
            tokens = prompt.split()
            masked_tokens = []
            i = 0
            while i < len(tokens):
                if random.random() < mask_rate:
                    # Determine mask size (but don't exceed remaining tokens)
                    size = min(random.choice(mask_size), len(tokens) - i)
                    masked_tokens.append("[MASK]")
                    i += size
                else:
                    masked_tokens.append(tokens[i])
                    i += 1
            masked_prompt = " ".join(masked_tokens)
        else:
            chars = list(prompt)
            masked_chars = []
            i = 0
            while i < len(chars):
                if random.random() < mask_rate:
                    # Determine mask size (but don't exceed remaining chars)
                    size = min(random.choice(mask_size), len(chars) - i)
                    masked_chars.append("[MASK]")
                    i += size
                else:
                    masked_chars.append(chars[i])
                    i += 1
            masked_prompt = "".join(masked_chars)
        
        message = f"Here is a prompt with masked sections:\n{masked_prompt}"
        response, [unmasked_prompt] = self.answer(message, self.model, temperature=temperature, tags=["unmasked_prompt"])
        return response, unmasked_prompt
        
class MaskedCrossoverAgent(Agent):
    def __init__(self, llm: LLMBase, model: str = "gemma3-27b"):
        super().__init__(llm, open("prompts/unmask_crossover.md", "r", encoding="utf-8").read())
        self.model = model
        
    def crossover(self, parent1, parent2, temperature: float = 0, mask_rate: float = 0.3, mask_size: range = range(1, 10)):
        """
        Creates a child prompt by intelligently combining elements from two parent prompts.
        
        Args:
            parent1: The first parent prompt
            parent2: The second parent prompt
            problem_statement: The problem these prompts are attempting to solve
            temperature: The temperature to use for generation
            mask_rate: The probability of masking a section of text
            mask_size: The range of token sizes to mask
            
        Returns:
            A tuple containing (raw_response, child_prompt)
        """
        # Apply masking to both parents
        unmask_agent = UnmaskMutationAgent(self.llm, self.model)
        masked_parent1 = unmask_agent.unmask_mutation(parent1.get_prompt(), 0, mask_rate, mask_size, True)[1]
        masked_parent2 = unmask_agent.unmask_mutation(parent2.get_prompt(), 0, mask_rate, mask_size, True)[1]
        
        message = f"""1. Parent prompt 1 with masked sections:
            {masked_parent1}

            2. Parent prompt 2 with masked sections:
            {masked_parent2}

            Please combine the prompts using the unmasked sections as a guide.
            """
        
        response, [child_prompt] = self.answer(message, self.model, temperature=temperature, tags=["child_prompt"])
        if "[MASK]" in child_prompt:
            raise ValueError("Crossover agent failed to generate a valid child prompt. It contains a [MASK] tag.")
        
        return response, child_prompt
    
class PhenotypeAgent(Agent):
    def __init__(self, llm: LLMBase, model: str = "gemma3-27b"):
        super().__init__(llm, PHENOTYPE_PROMPT)
        self.model = model

    def generate_phenotype(self, problem_prompt, temperature: float = .7):
        message = f"Please come up with a unique prompt for software that will solve the following problem: {problem_prompt}"
        response, [phenotype] = super().answer(message, self.model, temperature=temperature, tags=["prompt"])
        return response, phenotype
    
class GenotypeAgent(Agent):
    def __init__(self, llm: LLMBase, model: str = "gemma3-27b"):
        super().__init__(llm, GENOTYPE_PROMPT)
        self.model = model

    def generate_genotype(self, phenotype, temperature: float = 0):
        message = f"{phenotype}"
        response, [genotype, requirements] = super().answer(message, self.model, temperature=temperature, tags=["genotype_py", "requirements_txt"])
        return response, genotype, requirements if requirements else "pytest\n"