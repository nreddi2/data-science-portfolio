from pathlib import Path
import nbformat
from nbclient import NotebookClient

root = Path(__file__).resolve().parent
notebook = nbformat.read(root / "chess_outcomes.ipynb", as_version=4)
print("Running the notebook from top to bottom. Model fitting can take several minutes.", flush=True)
client = NotebookClient(notebook, timeout=1200, kernel_name="python3",
                        resources={"metadata": {"path": str(root)}})
client.execute()
destination = root / "chess_outcomes_rerun.ipynb"
nbformat.write(notebook, destination)
print(f"Finished: {destination}")
