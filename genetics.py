import os
import subprocess
import sys
import json

class Individual:
    def __init__(self, directory: str, idstr: str, fitness: float = 0):
        # Always store directory as an absolute path
        if os.path.isabs(directory):
            self.directory = directory
        else:
            self.directory = os.path.abspath(directory)
        self.fitness = fitness
        self.idstr = idstr
    
    def get_prompt(self):
        # reads self.directory/prompt.md
        with open(os.path.join(self.directory, "prompt.md"), "r", encoding="utf-8") as f:
            return f.read()
    def kill(self):
        # Extract the individual's ID from the path
        individual_id = os.path.basename(self.directory)
        
        # Get the absolute path to the dead_individuals directory
        base_dir = os.path.dirname(os.path.dirname(self.directory))
        destination = os.path.join(base_dir, "dead_individuals", individual_id)
        
        # Move the directory
        os.rename(self.directory, destination)
        
        # Update the directory attribute to the new absolute path
        self.directory = destination
        return True
    def test_fitness(self):
        print("Testing fitness")
        # Save current directory
        current_dir = os.getcwd()
        
        try:
            # Change to the individual's directory using absolute path
            os.chdir(self.directory)
            
            # Use absolute paths for the Python interpreter
            if sys.platform == "win32":
                venv_python = os.path.join(self.directory, "venv", "Scripts", "python.exe")
            else:
                venv_python = os.path.join(self.directory, "venv", "bin", "python")
            
            # Run fitness.py using absolute path
            fitness_path = os.path.join(self.directory, "fitness.py")
            output = subprocess.run([venv_python, fitness_path], 
                          capture_output=True, 
                          text=True,
                          check=False)
            print("output.stdout", output.stdout)
            self.load_fitness()
            
            return True
        except Exception as e:
            self.fitness = 0
            print(f"Individual {self.idstr} failed to test fitness: {e}")
            self.kill()
        finally:
            os.chdir(current_dir)
    def install_requirements(self):
        # Save current directory
        current_dir = os.getcwd()
        
        try:
            # Change to the individual's directory using absolute path
            os.chdir(self.directory)
            
            # Get Python path
            if sys.platform == "win32":
                venv_python = os.path.join(self.directory, "venv", "Scripts", "python.exe")
            else:
                venv_python = os.path.join(self.directory, "venv", "bin", "python")
            
            if not os.path.exists(venv_python):
                raise FileNotFoundError(f"Python executable not found at {venv_python}")
            
            # Get requirements.txt path from individual's directory
            requirements_path = os.path.join(self.directory, "requirements.txt")
            
            if not os.path.exists(requirements_path):
                raise FileNotFoundError(f"Requirements file not found at {requirements_path}")
            
            # Install requirements using python -m pip instead of direct pip executable
            print(f"Installing requirements from {requirements_path}...")
            result = subprocess.run(
                [venv_python, "-m", "pip", "install", "-r", requirements_path],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                print(f"Error installing requirements: {result.stderr}")
                raise RuntimeError(f"Failed to install requirements: {result.stderr}")
                
            print(f"Successfully installed requirements")
                          
        except Exception as e:
            print(f"Error in install_requirements: {str(e)}")
            raise
        finally:
            os.chdir(current_dir)

    def setup(self):
        current_dir = os.getcwd()
        
        try:
            # Ensure the directory exists
            if not os.path.exists(self.directory):
                raise FileNotFoundError(f"Individual directory not found: {self.directory}")
                
            # Change to the individual's directory using absolute path
            os.chdir(self.directory)
            
            # Create virtual environment
            print(f"Creating virtual environment in {self.directory}...")
            venv_result = subprocess.run([sys.executable, "-m", "venv", "venv"], 
                                        capture_output=True, 
                                        text=True,
                                        check=False)
            
            if venv_result.returncode != 0:
                print(f"Error creating venv: {venv_result.stderr}")
                raise RuntimeError(f"Failed to create virtual environment: {venv_result.stderr}")
                
            # Ensure pip is available by upgrading it first
            if sys.platform == "win32":
                python_exe = os.path.join(self.directory, "venv", "Scripts", "python.exe")
            else:
                python_exe = os.path.join(self.directory, "venv", "bin", "python")
                
            if not os.path.exists(python_exe):
                print(f"Python executable not found at {python_exe}")
                available_files = os.listdir(os.path.dirname(python_exe))
                print(f"Available files in {os.path.dirname(python_exe)}: {available_files}")
                raise FileNotFoundError(f"Python executable not found in the virtual environment")
                
            # Upgrade pip to ensure it's available and properly installed
            print(f"Upgrading pip in {self.directory}...")
            upgrade_pip = subprocess.run(
                [python_exe, "-m", "pip", "install", "--upgrade", "pip"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if upgrade_pip.returncode != 0:
                print(f"Error upgrading pip: {upgrade_pip.stderr}")
                # Continue anyway, as pip might still work
            
            # Install requirements
            self.install_requirements()
            
            # Copy fitness.py from environment using absolute paths
            src_fitness = os.path.join(current_dir, "environment", "fitness.py")
            
            # Check if the source fitness.py file exists
            if not os.path.exists(src_fitness):
                print(f"Source fitness.py not found at {src_fitness}")
                print(f"Current directory: {current_dir}")
                print(f"Environment directory content: {os.listdir(os.path.join(current_dir, 'environment')) if os.path.exists(os.path.join(current_dir, 'environment')) else 'Environment directory not found'}")
                raise FileNotFoundError(f"Source fitness.py not found at {src_fitness}")
                
            dst_fitness = os.path.join(self.directory, "fitness.py")
            print(f"Copying fitness.py from {src_fitness} to {dst_fitness}")
            with open(src_fitness, "r", encoding="utf-8") as src:
                with open(dst_fitness, "w", encoding="utf-8") as dst:
                    dst.write(src.read())
            
            # Test fitness
            self.test_fitness()
            
            return True

        finally:
            os.chdir(current_dir)
    def load_fitness(self):
        with open(os.path.join(self.directory, "data.json"), "r") as f:
            data = json.load(f)
        self.fitness = float(data["score"])
    
    def reset_attributes(self, prompt: str, genotype: str, requirements: str):
        current_dir = os.getcwd()
        
        try:
            os.chdir(self.directory)
            
            # Write files using absolute paths
            with open(os.path.join(self.directory, "prompt.md"), "w", encoding="utf-8") as f:
                f.write(prompt)
            with open(os.path.join(self.directory, "genotype.py"), "w", encoding="utf-8") as f:
                f.write(genotype)
            with open(os.path.join(self.directory, "requirements.txt"), "w", encoding="utf-8") as f:
                f.write(requirements)
                
            # Install requirements and test fitness
            self.install_requirements()
            self.test_fitness()
        finally:
            os.chdir(current_dir)