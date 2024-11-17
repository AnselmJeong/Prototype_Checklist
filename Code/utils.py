from IPython.display import Image, display
from langgraph.graph.state import CompiledStateGraph
from textwrap import fill

def display_graph(app: CompiledStateGraph):
    """Display the graph of the app.
    
    Args:
        app: The langgraph compiled app to display the graph of.
    """
    display(Image(app.get_graph(xray=True).draw_mermaid_png()))
    
    
def fprint(text: str, width: int = 80):
    """Print a text with line breaks at a given width."""
    print(fill(text, width=width))