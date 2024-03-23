import spacy
import networkx as nx
import plotly.graph_objects as go

def extract_relations(doc):
    relations = []
    for token in doc:
        if token.dep_ in ["nsubj", "dobj", "pobj", "attr", "appos"]:
            head = token.head
            if head.pos_ in ["VERB", "AUX", "NOUN", "ADJ"]:
                relation = (token.text, head.text, head.pos_)
                relations.append(relation)
    return relations

def create_knowledge_graph(text):
    doc = nlp(text)
    relations = extract_relations(doc)
    graph = nx.DiGraph()

    for relation in relations:
        entity, head, pos = relation
        if pos == "VERB" or pos == "AUX":
            graph.add_edge(entity, head, label=head)
        else:
            graph.add_edge(head, entity, label=pos)

    return graph

# Load the spaCy English model
nlp = spacy.load("en_core_web_sm")

# Get the file path from the user
file_path = input("Enter the path to the text file: ")

# Read the text from the file
with open(file_path, "r") as file:
    text = file.read()

# Create the knowledge graph
knowledge_graph = create_knowledge_graph(text)

# Create the Plotly figure
fig = go.Figure(data=[go.Scatter3d(
    x=[],
    y=[],
    z=[],
    mode='markers',
    marker=dict(
        size=12,
        color=[],
        opacity=0.8
    ),
    text=[],
    hoverinfo='text'
)])

# Add nodes to the figure
pos = nx.spring_layout(knowledge_graph, dim=3, seed=42)
for node in knowledge_graph.nodes():
    x, y, z = pos[node]
    fig.add_trace(go.Scatter3d(
        x=[x],
        y=[y],
        z=[z],
        mode='markers+text',
        marker=dict(size=20, color='skyblue'),
        text=[node],
        textposition='middle center',
        hoverinfo='text'
    ))

# Add edges to the figure
edge_traces = []
edge_labels = nx.get_edge_attributes(knowledge_graph, 'label')
for edge in knowledge_graph.edges():
    node1, node2 = edge
    x1, y1, z1 = pos[node1]
    x2, y2, z2 = pos[node2]
    edge_trace = go.Scatter3d(
        x=[x1, x2],
        y=[y1, y2],
        z=[z1, z2],
        mode='lines',
        line=dict(color='gray', width=2),
        hoverinfo='none'
    )
    edge_traces.append(edge_trace)

    # Add edge labels
    x_mid = (x1 + x2) / 2
    y_mid = (y1 + y2) / 2
    fig.add_annotation(
        x=x_mid,
        y=y_mid,
        text=edge_labels[edge],
        showarrow=False,
        font=dict(size=10, color='red'),
        opacity=0.7
    )

fig.add_traces(edge_traces)

# Configure the layout
fig.update_layout(
    title="Interactive Knowledge Graph",
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False)
    ),
    showlegend=False,
    hoverlabel=dict(font=dict(size=12))
)

# Show the interactive plot
fig.show()