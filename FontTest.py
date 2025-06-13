import matplotlib.font_manager as fm

# Find system fonts (including those within the venv's font directory if you copied it there)
font_paths = fm.findSystemFonts(fontpaths=None, fontext="ttf")

# Print the list of found font paths
for path in font_paths:
    print(path)