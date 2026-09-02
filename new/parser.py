from pydantic import BaseModel, Field

class Parser(BaseModel):
    """ Checks the input_file and produce Map/graph object."""
    

    def parse(self, input_file: str) -> None:
        """ Parse the input file and process its contents."""
        try:
            with open(input_file, 'r') as file:
                content = file.readlines()
        except OSError as e:
            print(f"Error reading file {input_file}: {e}")

        for line in content:
            if line.startswith("#") or line.strip() == "":
                continue  # Skip comment lines and empty lines
            elif line.startswith("nb_drones"):
