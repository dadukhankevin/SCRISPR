import random
from typing import List, Callable, Tuple
from genetics import Individual

def random_selection(individuals: List[Individual], k: int = 2) -> List[Individual]:
    """
    Randomly selects k individuals from the population.
    
    Args:
        individuals: List of individuals to select from
        k: Number of individuals to select
        
    Returns:
        List of selected individuals
    """
    return random.sample(individuals, min(k, len(individuals)))

def tournament_selection(individuals: List[Individual], tournament_size: int = 3, k: int = 2) -> List[Individual]:
    """
    Selects k individuals using tournament selection.
    
    Args:
        individuals: List of individuals to select from
        tournament_size: Number of individuals in each tournament
        k: Number of individuals to select
        
    Returns:
        List of selected individuals
    """
    selected = []
    for _ in range(k):
        tournament = random.sample(individuals, min(tournament_size, len(individuals)))
        winner = max(tournament, key=lambda ind: ind.fitness)
        selected.append(winner)
    return selected

def roulette_wheel_selection(individuals: List[Individual], k: int = 2) -> List[Individual]:
    """
    Selects k individuals using fitness-proportionate (roulette wheel) selection.
    
    Args:
        individuals: List of individuals to select from
        k: Number of individuals to select
        
    Returns:
        List of selected individuals
    """
    # Handle case where all fitnesses are 0
    total_fitness = sum(ind.fitness for ind in individuals)
    if total_fitness == 0:
        return random.sample(individuals, min(k, len(individuals)))
    
    # Calculate selection probabilities
    selection_probs = [ind.fitness / total_fitness for ind in individuals]
    
    # Select k individuals
    return random.choices(individuals, weights=selection_probs, k=k)

def rank_selection(individuals: List[Individual], k: int = 2) -> List[Individual]:
    """
    Selects k individuals using rank-based selection.
    
    Args:
        individuals: List of individuals to select from
        k: Number of individuals to select
        
    Returns:
        List of selected individuals
    """
    # Sort individuals by fitness
    sorted_individuals = sorted(individuals, key=lambda ind: ind.fitness, reverse=True)
    
    # Assign ranks (higher rank = higher selection probability)
    ranks = list(range(1, len(sorted_individuals) + 1))
    ranks.reverse()  # Highest fitness gets highest rank
    
    # Select based on ranks
    return random.choices(sorted_individuals, weights=ranks, k=k)

def elitism_selection(individuals: List[Individual], elite_count: int = 1, k: int = 2) -> List[Individual]:
    """
    Selects the elite_count best individuals and k-elite_count random individuals.
    
    Args:
        individuals: List of individuals to select from
        elite_count: Number of top individuals to always select
        k: Total number of individuals to select
        
    Returns:
        List of selected individuals
    """
    if not individuals:
        return []
    
    # Sort by fitness (descending)
    sorted_individuals = sorted(individuals, key=lambda ind: ind.fitness, reverse=True)
    
    # Select elites
    elites = sorted_individuals[:min(elite_count, len(sorted_individuals))]
    
    # Select remaining individuals randomly
    remaining = random.sample(sorted_individuals[elite_count:], 
                             min(k - len(elites), len(sorted_individuals) - elite_count))
    
    return elites + remaining

def diversity_selection(individuals: List[Individual], k: int = 2, 
                       diversity_measure: Callable[[Individual, Individual], float] = None) -> List[Individual]:
    """
    Selects k diverse individuals based on a diversity measure.
    
    Args:
        individuals: List of individuals to select from
        k: Number of individuals to select
        diversity_measure: Function that measures diversity between two individuals
                          (defaults to a simple random selection if None)
        
    Returns:
        List of selected individuals
    """
    if not diversity_measure or len(individuals) <= k:
        return random.sample(individuals, min(k, len(individuals)))
    
    selected = [random.choice(individuals)]
    
    while len(selected) < k:
        # Find individual with maximum average distance to already selected individuals
        max_diversity = -1
        most_diverse = None
        
        for ind in individuals:
            if ind in selected:
                continue
                
            # Calculate average diversity to already selected individuals
            avg_diversity = sum(diversity_measure(ind, sel) for sel in selected) / len(selected)
            
            if avg_diversity > max_diversity:
                max_diversity = avg_diversity
                most_diverse = ind
        
        if most_diverse:
            selected.append(most_diverse)
        else:
            # Fallback if no diverse individual found
            remaining = [ind for ind in individuals if ind not in selected]
            if remaining:
                selected.append(random.choice(remaining))
            else:
                break
                
    return selected

def parent_pairs_selection(individuals: List[Individual], 
                          selection_func: Callable[[List[Individual], int], List[Individual]], 
                          num_pairs: int = 1) -> List[Tuple[Individual, Individual]]:
    """
    Creates num_pairs of parent pairs using the provided selection function.
    
    Args:
        individuals: List of individuals to select from
        selection_func: Function to select individuals
        num_pairs: Number of parent pairs to create
        
    Returns:
        List of parent pairs (tuples of two individuals)
    """
    pairs = []
    for _ in range(num_pairs):
        parents = selection_func(individuals, k=2)
        # Ensure we have exactly 2 parents
        if len(parents) == 2:
            pairs.append((parents[0], parents[1]))
        elif len(parents) == 1:
            # If only one parent available, duplicate it
            pairs.append((parents[0], parents[0]))
        else:
            # Skip this pair if no parents available
            continue
    return pairs
