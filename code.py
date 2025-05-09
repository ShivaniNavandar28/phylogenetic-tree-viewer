import streamlit as st
import sys
import subprocess
from importlib.metadata import version, PackageNotFoundError

# Dependency check function
def check_dependencies():
    required = {
        'biopython': '1.81',
        'streamlit': '1.32.0',
        'pyvis': '0.3.2',
        'plotly': '5.18.0',
        'pandas': '2.1.4',
        'matplotlib': '3.8.2',
        'seaborn': '0.13.0',
        'streamlit-lottie': '0.0.5',
        'requests': '2.31.0'
    }
    
  missing = []
    for package, req_version in required.items():
        try:
            installed = version(package)
            if installed < req_version:
                missing.append(f"{package}>={req_version} (installed: {installed})")
        except PackageNotFoundError:
            missing.append(f"{package}>={req_version}")

    if missing:
        st.error("Missing or outdated dependencies detected!")
        st.code("pip install --upgrade " + " ".join(missing))
        st.stop()
# Check dependencies before proceeding
check_dependencies()

from Bio import Phylo
from io import StringIO
import streamlit.components.v1 as components
import random
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import base64
from streamlit_lottie import st_lottie
import requests
import sys

# -------------------------------
# Pyvis Network Import with Error Handling
# -------------------------------
try:
    import pyvis
    from pyvis.network import Network
    PYVIS_AVAILABLE = True
except (ImportError, AttributeError) as e:
    st.warning(f"Pyvis visualization unavailable: {str(e)}. Using alternative methods.")
    PYVIS_AVAILABLE = False
    Network = None

# -------------------------------
# Utility Functions
# -------------------------------
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def download_button(content, filename, label):
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{label}</a>'
    st.markdown(href, unsafe_allow_html=True)

# -------------------------------
# Visualization Functions
# -------------------------------
def visualize_with_plotly(newick_str):
    st.write("### 🌳 Tree Visualization (Plotly)")
    tree = Phylo.read(StringIO(newick_str), "newick")
    
    # Create node and edge data
    edges = []
    node_names = set()
    
    for clade in tree.find_clades():
        node_name = clade.name if clade.name else f"Node_{id(clade)}"
        node_names.add(node_name)
        for child in clade:
            child_name = child.name if child.name else f"Node_{id(child)}"
            edges.append((node_name, child_name))
            node_names.add(child_name)
    
    # Create network graph
    fig = go.Figure()
    
    # Add edges
    for edge in edges:
        fig.add_trace(go.Scatter(
            x=[0, 1],  # Simplified coordinates
            y=[0, 1],
            mode='lines',
            line=dict(width=2, color='gray'),
            hoverinfo='none'
        ))
    
    # Add nodes
    node_positions = {name: (random.random(), random.random()) for name in node_names}
    
    for name in node_names:
        x, y = node_positions[name]
        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers+text',
            marker=dict(size=20, color='blue'),
            text=name,
            textposition="top center",
            name=name
        ))
    
    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600,
        margin=dict(l=20, r=20, b=20, t=40)
    )
    st.plotly_chart(fig, use_container_width=True)

def visualize_phylo_tree(newick_str):
    if PYVIS_AVAILABLE:
        try:
            tree = Phylo.read(StringIO(newick_str), "newick")
            net = Network(height="600px", width="100%", bgcolor="#eaf6f6", font_color="black")
            net.barnes_hut()

            for clade in tree.find_clades():
                node_name = clade.name if clade.name else f"Node_{id(clade)}"
                net.add_node(node_name, label=node_name, shape="ellipse", color="#2980b9")

            for clade in tree.find_clades():
                for child in clade:
                    parent_name = clade.name if clade.name else f"Node_{id(clade)}"
                    child_name = child.name if child.name else f"Node_{id(child)}"
                    net.add_edge(parent_name, child_name)

            net.set_options("""
            var options = {
              "nodes": {"font": {"size": 20}},
              "edges": {"smooth": false},
              "physics": {"barnesHut": {"gravitationalConstant": -8000, "springLength": 100}},
              "interaction": {"hover": true, "tooltipDelay": 100}
            }
            """)
            net.save_graph("phylogenetic_tree.html")
            with open("phylogenetic_tree.html", 'r', encoding='utf-8') as f:
                html_content = f.read()
                components.html(html_content, height=600)
        except Exception as e:
            st.warning(f"Pyvis visualization failed: {str(e)}. Falling back to alternative method.")
            visualize_with_plotly(newick_str)
    else:
        visualize_with_plotly(newick_str)

# -------------------------------
# Application Pages
# -------------------------------
def show_home():
    st.title("👩‍🔬 Welcome to the Phylogenetic Tool")
    lottie_animation = load_lottie_url("https://assets8.lottiefiles.com/packages/lf20_0yfsb3a1.json")
    if lottie_animation:
        st_lottie(lottie_animation, height=200)
    else:
        st.warning("⚠️ Lottie animation failed to load.")

    st.header("📌 Author")
    st.image("https://media.licdn.com/dms/image/v2/D4D03AQEgnt4XvXhF4w/profile-displayphoto-shrink_800_800/B4DZawFXQhG8Ac-/0/1746710919292?e=1752105600&v=beta&t=6XpldOaEle1lITOL3VLe_t7_NjlwkKQtrjqFnuadKh4", width=150)
    st.markdown("**Shivani Sujit Navandar**")
    st.markdown("[LinkedIn Profile](https://www.linkedin.com/in/shivani-navandar-3b8450291)")
    st.markdown("🎓 M.Sc. Bioinformatics, DES Pune University")
    st.markdown("🔬 Focused on functional genomics and computational biology")
    st.markdown("💻 Skilled in Python, R, and bioinformatics tools")

    st.header("🌐 About This Web Server")
    st.markdown("""
    - Visualize & simulate phylogenetic trees.
    - Upload FASTA or simulate divergence.
    - Interactive trees, charts & insights.
    - Modern UI with animations.
    """)

    st.header("👨‍🏫 Mentor")
    st.image("https://media.licdn.com/dms/image/v2/D5603AQF9gsU7YBjWVg/profile-displayphoto-shrink_800_800/B56ZZI.WrdH0Ac-/0/1744981029051?e=1752105600&v=beta&t=NY99PWbYHr9Wi8VkPoMtFBfLhqvNl1uLKgH1_hetXY0", width=150)
    st.markdown("**Dr. Kushagra Kashyap**")
    st.markdown("[LinkedIn](https://www.linkedin.com/in/dr-kushagra-kashyap-b230a3bb/)")
    st.markdown("Assistant Professor, DES Pune University")

    st.header("📬 Feedback")
    st.markdown("Email: 3522411011@despu.edu.in")

def construct_tree_from_fasta():
    uploaded_file = st.file_uploader("📁 Upload FASTA File", type=["fasta", "fa"])
    if uploaded_file is not None:
        fasta_data = uploaded_file.read().decode("utf-8")
        st.write("### 📄 Uploaded FASTA File Content")
        st.text(fasta_data)

        simulated_newick = "((A:0.2,B:0.3):0.1,(C:0.4,D:0.5):0.2);"
        st.write("### 🌳 Simulated Tree from FASTA (placeholder)")
        st.code(simulated_newick)
        download_button(simulated_newick, "tree_from_fasta.newick", "📥 Download Simulated Tree")
        visualize_phylo_tree(simulated_newick)

def simulate_evolutionary_divergence():
    species = ["Human", "Chimpanzee", "Gorilla", "Orangutan"]
    mutations = random.sample(range(10, 100), 4)

    newick_str = f"(({species[0]}:{mutations[0]},{species[1]}:{mutations[1]}):0.2,({species[2]}:{mutations[2]},{species[3]}:{mutations[3]}):0.3);"
    st.write("### 🧬 Simulated Phylogenetic Tree (Newick Format):")
    st.code(newick_str)
    download_button(newick_str, "tree.newick", "📥 Download Newick Format")
    visualize_phylo_tree(newick_str)
    plot_mutation_bar_chart(species, mutations)
    plot_heatmap(species, mutations)
    plot_pie_chart(species, mutations)
    generate_ai_insight(species, mutations)

def plot_mutation_bar_chart(species, mutations):
    st.write("### 📊 Mutation Rates Bar Chart")
    df = pd.DataFrame({'Species': species, 'Mutations': mutations})
    fig = px.bar(df, x='Species', y='Mutations', color='Species', title='Genetic Divergence Simulation', height=400)
    st.plotly_chart(fig)

def plot_heatmap(species, mutations):
    st.write("### 🔥 Heatmap of Divergence Scores")
    df = pd.DataFrame([mutations], columns=species)
    fig, ax = plt.subplots()
    sns.heatmap(df, annot=True, cmap="coolwarm", cbar=True)
    st.pyplot(fig)

def plot_pie_chart(species, mutations):
    st.write("### 🧬 Mutation Contribution by Species")
    df = pd.DataFrame({'Species': species, 'Mutations': mutations})
    fig = px.pie(df, values='Mutations', names='Species', title='Relative Divergence', hole=0.3)
    st.plotly_chart(fig)

def generate_ai_insight(species, mutations):
    max_idx = mutations.index(max(mutations))
    min_idx = mutations.index(min(mutations))
    st.write("### 🧠 Evolution Insight")
    st.markdown(f"The most genetically divergent species is **{species[max_idx]}**, while **{species[min_idx]}** remains closest to the ancestral root. Evolutionary patterns suggest environmental or behavioral pressures influencing divergence rates.")

def show_evolution_stats():
    st.write("### 📈 Evolutionary Insights")
    stats = {
        "Avg. Divergence Time (MYA)": 5.4,
        "Total Species Analyzed": 4,
        "Most Divergent Species": "Orangutan",
        "Closest Relation": "Human - Chimpanzee",
        "Tree Topology Simulated": "Yes",
        "Divergence Method": "Randomized Score-Based"
    }
    for key, value in stats.items():
        st.markdown(f"**{key}:** {value}")

def show_acknowledgement():
    st.title("🌟 Acknowledgements")
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 25px; border-radius: 10px; border-left: 5px solid #0066cc; color: black;">
    
    ### I sincerely acknowledge the support and contributions that helped make this project possible:

    *Mentorship & Guidance*  
    - My deepest gratitude to <span style="color: #1f77b4;"><strong>Dr. Kushagra Kashyap</strong></span> (Assistant Professor, DES Pune University) for his invaluable guidance, constant encouragement, and expert supervision throughout this project.
    
    *Institutional Support*  
    - The <span style="color: #1f77b4;"><strong>Department of Bioinformatics, DES Pune University</strong></span> for providing the academic environment and resources necessary for this research.
    - The university administration for fostering an ecosystem of innovation and research excellence.

    *Technical Resources*  
    - The <span style="color: #1f77b4;"><strong>Python and Streamlit</strong></span> developer communities for their powerful open-source tools that made this application possible.
    - <span style="color: #1f77b4;"><strong>BioPython</strong></span> and other bioinformatics libraries that inspired our analytical approaches.
    
    *Personal Support*  
    - My family and friends for their unwavering support and patience throughout this journey.

    <div style="text-align: center; margin-top: 30px; font-style: italic; color: #555;">
    "Knowledge grows when shared - we gratefully stand on the shoulders of those who came before us,<br>
    and hope this tool will support those who follow in bioinformatics research."
    </div>
    
    </div>
    """, unsafe_allow_html=True)

# -------------------------------
# Main Application
# -------------------------------
def run_phylo_app():
    st.markdown("""
        <h1 style='text-align: center; font-size: 40px; color: #2c3e50;'>🌿 Phylogenetic Tree Viewer & Evolution Simulator</h1>
        <p style='text-align: center; font-size:18px; color: #34495e;'>Explore interactive evolutionary trees, mutation divergence, and simulated phylogeny with visual insights and downloadable formats.</p>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["🏠 Home", "📂 Upload FASTA", "🧬 Simulate Divergence", "📊 Evolution Stats", "🙏 Acknowledgement"])

    with tabs[0]: show_home()
    with tabs[1]: construct_tree_from_fasta()
    with tabs[2]: simulate_evolutionary_divergence()
    with tabs[3]: show_evolution_stats()
    with tabs[4]: show_acknowledgement()

if __name__ == "__main__":
    run_phylo_app()
