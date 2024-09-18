from matplotlib import pyplot as plt

plt.rcParams.update(
    {
        "axes.facecolor": "#1d1d1d",
        "figure.facecolor": "#1d1d1d",
        "text.color": "white",
        "axes.labelcolor": "white",
        "xtick.color": "white",
        "ytick.color": "white",
        "axes.edgecolor": "white",
        "axes.titlecolor": "white",
        "axes.titlepad": 17,
        "font.size": 15,
        "xtick.labelsize": 13,
        "ytick.labelsize": 13,
    }
)
site_palette = [plt.get_cmap("Spectral", 7)(i) for i in range(7)]
cluster_palette = ["#ed6a5a", "#f4f1bb", "#9bc1bc"]
cluster_palette_4 = ["#335c67", "#fff3b0", "#e09f3e", "#9e2a2b"]

figwidth = 8
textsize = 15
