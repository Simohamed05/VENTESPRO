import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

def plot_sales(df):
    """Affiche l'évolution des ventes."""
    fig = px.line(df, x=df.index, y="Ventes", title="📈 Évolution des Ventes")
    return fig

def plot_correlation(df):
    """Affiche la heatmap des corrélations."""
    fig, ax = plt.subplots(figsize=(8,6))
    sns.heatmap(df.corr(), annot=True, cmap="coolwarm", ax=ax)
    return fig
