import streamlit as st
import sys
import subprocess
from importlib.metadata import version, PackageNotFoundError

# Dependency check function
def check_dependencies():
    required = {
        'biopython': '1.81',
        'streamlit': '1.32.0',
        'pyvis': '0.3.1',
        'plotly': '5.18.0',
        'pandas': '2.1.4',
        'matplotlib': '3.10.0',
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

# Pyvis Network Import
try:
    import pyvis
    from pyvis.network import Network
    PYVIS_AVAILABLE = True
except (ImportError, AttributeError) as e:
    st.warning(f"Pyvis visualization unavailable: {str(e)}. Using alternative methods.")
    PYVIS_AVAILABLE = False
    Network = None

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
    custom_css = """
    <style>
    .custom-download-button a {
        display: inline-block;
        font-size: 16px;
        font-weight: bold;
        color: white;
        background-color: #1f77b4;
        padding: 10px 20px;
        text-decoration: none;
        border-radius: 8px;
        transition: background-color 0.3s ease;
    }
    .custom-download-button a:hover {
        background-color: #145a86;
    }
    </style>
    """
    href = f'<div class="custom-download-button">{custom_css}<a href="data:file/txt;base64,{b64}" download="{filename}">{label}</a></div>'
    st.markdown(href, unsafe_allow_html=True)

# -------------------------------
# Visualization 
# -------------------------------
def visualize_with_plotly(newick_str):
    st.write("### 🌳 Tree Visualization (Plotly)")
    tree = Phylo.read(StringIO(newick_str), "newick")
    edges = []
    node_names = set()
    for clade in tree.find_clades():
        node_name = clade.name if clade.name else f"Node_{id(clade)}"
        node_names.add(node_name)
        for child in clade:
            child_name = child.name if child.name else f"Node_{id(child)}"
            edges.append((node_name, child_name))
            node_names.add(child_name)
    fig = go.Figure()
    node_positions = {name: (random.random(), random.random()) for name in node_names}
    for edge in edges:
        fig.add_trace(go.Scatter(
            x=[node_positions[edge[0]][0], node_positions[edge[1]][0]],
            y=[node_positions[edge[0]][1], node_positions[edge[1]][1]],
            mode='lines',
            line=dict(width=2, color='gray'),
            hoverinfo='none'
        ))
    for name in node_names:
        x, y = node_positions[name]
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
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

# -------------------------------
# Visualization with Pyvis  
# -------------------------------
def visualize_phylo_tree(newick_str):
    if PYVIS_AVAILABLE:
        try:
            tree = Phylo.read(StringIO(newick_str), "newick")
            net = Network(height="600px", width="100%", bgcolor="#f4faff", font_color="black")
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
            st.warning(f"Pyvis visualization failed: {str(e)}. Falling back to Plotly.")
            visualize_with_plotly(newick_str)
    else:
        visualize_with_plotly(newick_str)

# -------------------------------
# Home Page 
# -------------------------------
def show_home():
    st.title("👩‍🔬 Welcome to the Phylogenetic Tool")

    lottie_animation = load_lottie_url("https://assets1.lottiefiles.com/packages/lf20_tno6cg2w.json")
    if lottie_animation:
        st_lottie(lottie_animation, height=200)
    else:
        st.warning("⚠️ Lottie animation failed to load.")

    st.header("📌 Author")
    st.image("https://media.licdn.com/dms/image/v2/D4D03AQEgnt4XvXhF4w/profile-displayphoto-shrink_800_800/B4DZawFXQhG8Ac-/0/1746710919292?e=1752105600&v=beta&t=6XpldOaEle1lITOL3VLe_t7_NjlwkKQtrjqFnuadKh4", width=150)
    st.markdown("**Shivani Sujit Navandar**  \n[LinkedIn Profile](https://www.linkedin.com/in/shivani-navandar-3b8450291)  \n🎓 M.Sc. Bioinformatics, DES Pune University  \n🔬 Functional genomics & computational biology  \n💻 Python, R, and bioinformatics tools")

    st.header("🌐 About This Web Server")
    st.markdown("""
    <div style='background-color:#ecfaff;padding:15px;border-radius:10px;line-height:1.7; color:black;'>
        <p>This web server is designed to empower researchers, educators, and students in exploring evolutionary biology through intuitive tools.</p>
        <ul style="list-style-type: '🧬 '; font-size: 17px; padding-left: 20px;">
            <li>Upload raw FASTA sequences and automatically construct phylogenetic trees</li>
            <li>Simulate species divergence and explore genetic distances visually</li>
            <li>Download tree files in Newick format for publication or further analysis</li>
            <li>Enjoy beautiful data visualizations powered by Plotly and Pyvis</li>
            <li>Experience modern, responsive design with Lottie animations</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


    st.header("👨‍🏫 Mentor")
    st.image("https://media.licdn.com/dms/image/v2/D5603AQF9gsU7YBjWVg/profile-displayphoto-shrink_800_800/B56ZZI.WrdH0Ac-/0/1744981029051?e=1752105600&v=beta&t=NY99PWbYHr9Wi8VkPoMtFBfLhqvNl1uLKgH1_hetXY0", width=150)
    st.markdown("**Dr. Kushagra Kashyap**  \n[LinkedIn](https://www.linkedin.com/in/dr-kushagra-kashyap-b230a3bb/)  \nAssistant Professor, DES Pune University")

    st.header("📬 Feedback")
    st.markdown("Email: 3522411011@despu.edu.in")
    st.markdown("Github: https://github.com/ShivaniNavandar28")

# -------------------------------
# FASTA Upload Page
# -------------------------------
from Bio import SeqIO
from Bio.Align import PairwiseAligner
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor
from io import StringIO

def construct_tree_from_fasta():
    st.write("## 📂 Upload FASTA File")
    lottie = load_lottie_url("https://assets6.lottiefiles.com/packages/lf20_usmfx6bp.json")
    if lottie:
        st_lottie(lottie, height=150)

    uploaded_file = st.file_uploader("Choose a FASTA file (.fasta or .fa)", type=["fasta", "fa"])
    if uploaded_file:
        fasta_data = uploaded_file.read().decode("utf-8")
        st.text_area("📄 FASTA File Content", fasta_data, height=200)

        try:
            # Parse sequences
            records = list(SeqIO.parse(StringIO(fasta_data), "fasta"))
            if len(records) < 2:
                st.warning("⚠️ Please upload a FASTA file with at least 2 sequences.")
                return

            # Compute pairwise distances using identity score
            aligner = PairwiseAligner()
            aligner.mode = 'global'

            names = [rec.id for rec in records]
            n = len(names)
            matrix = [[0.0]*n for _ in range(n)]

            for i in range(n):
                for j in range(i):
                    score = aligner.score(records[i].seq, records[j].seq)
                    max_len = max(len(records[i]), len(records[j]))
                    distance = 1 - (score / max_len)
                    matrix[i][j] = matrix[j][i] = distance

            dm = DistanceMatrix(names, matrix)
            constructor = DistanceTreeConstructor()
            tree = constructor.nj(dm)

            # Show and download Newick
            output = StringIO()
            Phylo.write(tree, output, "newick")
            newick_tree = output.getvalue().strip()

            st.write("### 🌿 Phylogenetic Tree (Biopython, Pairwise)")
            st.code(newick_tree)
            download_button(newick_tree, "phylo_from_fasta.newick", "📥 Download Tree (Newick Format)")
            visualize_phylo_tree(newick_tree)

        except Exception as e:
            st.error(f"❌ Error generating tree: {str(e)}")

# -------------------------------
# Simulate Divergence Page
# -------------------------------
def simulate_evolutionary_divergence():
    st.write("## 🧬 Simulate Evolutionary Divergence")

    # Load and show animated header
    lottie = load_lottie_url("https://assets6.lottiefiles.com/private_files/lf30_ed9qppro.json")  # branching
    if lottie:
        st_lottie(lottie, height=200)

    species = ["Human", "Chimpanzee", "Gorilla", "Orangutan"]
    mutations = random.sample(range(10, 100), 4)

    newick_str = f"(({species[0]}:{mutations[0]},{species[1]}:{mutations[1]}):0.2,({species[2]}:{mutations[2]},{species[3]}:{mutations[3]}):0.3);"

    st.markdown("""
    <div style='background-color: #f0f8ff; padding: 20px; border-radius: 10px;'>
        <h4 style='color: #2c3e50;'>Generated Newick Tree:</h4>
    </div>
    """, unsafe_allow_html=True)
    st.code(newick_str)

    download_button(newick_str, "simulated_tree.newick", "📥 Download Newick Format")

    # Mutation metrics
    st.markdown("### 🔢 Mutation Distances per Species")
    col1, col2, col3, col4 = st.columns(4)
    for i, col in enumerate([col1, col2, col3, col4]):
        col.metric(label=species[i], value=f"{mutations[i]}")

    # Visualize tree
    visualize_phylo_tree(newick_str)

    # Show animated divider
    divider_lottie = load_lottie_url("https://assets1.lottiefiles.com/packages/lf20_j1adxtyb.json")
    if divider_lottie:
        st_lottie(divider_lottie, height=100)

    # Visualizations
    plot_mutation_bar_chart(species, mutations)
    plot_heatmap(species, mutations)
    plot_pie_chart(species, mutations)

    # Insight
    generate_ai_insight(species, mutations)

# -------------------------------
# Evolution Stats Page
# -------------------------------
def show_evolution_stats():
    st.write("## 📈 Evolutionary Statistics")
    lottie = load_lottie_url("https://assets6.lottiefiles.com/packages/lf20_urbk83vw.json")
    if lottie:
        st_lottie(lottie, height=150)
    
    stats = {
        "Avg. Divergence Time (MYA)": 5.4,
        "Total Species Analyzed": 4,
        "Most Divergent Species": "Orangutan",
        "Closest Relation": "Human - Chimpanzee",
        "Tree Topology Simulated": "Yes",
        "Divergence Method": "Randomized Score-Based"
    }
    for k, v in stats.items():
        st.markdown(f"**{k}:** {v}")

# -------------------------------
# Bar Chart for Mutation Rates
# -------------------------------
def plot_mutation_bar_chart(species, mutations):
    st.write("### 📊 Mutation Rates Bar Chart")
    df = pd.DataFrame({'Species': species, 'Mutations': mutations})
    fig = px.bar(df, x='Species', y='Mutations', color='Species', title='Genetic Divergence Simulation', height=400)
    st.plotly_chart(fig)

# -------------------------------
# Heatmap of Divergence Scores
# -------------------------------
def plot_heatmap(species, mutations):
    st.write("### 🔥 Heatmap of Divergence Scores")
    df = pd.DataFrame([mutations], columns=species)
    fig, ax = plt.subplots()
    sns.heatmap(df, annot=True, cmap="coolwarm", cbar=True)
    st.pyplot(fig)

# -------------------------------
# Pie Chart of Contributions
# -------------------------------
def plot_pie_chart(species, mutations):
    st.write("### 🧬 Mutation Contribution by Species")
    df = pd.DataFrame({'Species': species, 'Mutations': mutations})
    fig = px.pie(df, values='Mutations', names='Species', title='Relative Divergence', hole=0.3)
    st.plotly_chart(fig)

# -------------------------------
# AI-like Summary
# -------------------------------
def generate_ai_insight(species, mutations):
    max_idx = mutations.index(max(mutations))
    min_idx = mutations.index(min(mutations))
    st.write("### 🧠 Evolution Insight")
    st.markdown(f"""
    - The most genetically divergent species is **{species[max_idx]}**
    - The closest to ancestral root is **{species[min_idx]}**
    - Observations suggest environmental or behavioral pressures may explain this divergence
    """)

# -----------------
# Acknowledgements 
# -----------------
def show_acknowledgement():
    st.title("🙏 Acknowledgements")

    st.markdown("""
    <style>
    .ack-box {
        background-color: #f9fcff;
        padding: 25px;
        border-radius: 12px;
        border-left: 6px solid #2980b9;
        box-shadow: 0 0 8px rgba(0, 0, 0, 0.05);
        color: #2c3e50;
    }
    .ack-box h3 {
        margin-top: 20px;
        color: #2c3e50;
    }
    .ack-box ul {
        padding-left: 20px;
        margin-top: 10px;
    }
    .ack-box li {
        margin-bottom: 5px;
    }
    </style>

    <div class="ack-box">
        <h3>📚 Academic Guidance</h3>
        <ul>
            <li><strong>Dr. Kushagra Kashyap</strong> — For providing mentorship, continuous encouragement, and research direction.</li>
            <li><strong>DES Pune University</strong> — For nurturing a culture of innovation and providing an ideal research environment.</li>
        </ul>

        <h3>🧠 Project Contributions</h3>
        <p>This project was developed as part of a bioinformatics initiative, integrating knowledge from molecular biology, computational genomics, and data visualization.</p>

        <h3>💻 Technical Foundation</h3>
        <ul>
            <li><strong>Python, Streamlit</strong> — For rapid app development</li>
            <li><strong>BioPython</strong> — For sequence parsing, alignment and phylogenetics</li>
            <li><strong>Plotly, Pyvis</strong> — For building interactive and meaningful data visualizations</li>
        </ul>

        <h3>💖 Personal Note</h3>
        <p>Special thanks to my family and peers who supported me during this journey. This work reflects the collective effort, shared learning, and the spirit of open science.</p>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------
# Main App Runner
# -------------------------------
def run_phylo_app():
    # Global CSS Styles
    st.markdown("""
    <style>
    body {
        background: linear-gradient(to bottom right, #f0faff, #e0f7ff);
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    </style>
    """, unsafe_allow_html=True)

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
