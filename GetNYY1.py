import matplotlib.pyplot as plt
import matplotlib.font_manager

# (If you added the font to the Matplotlib font directory)
# Delete the font cache to rebuild it
# import shutil
# cache_dir = matplotlib.get_cachedir()
# if cache_dir:
#    shutil.rmtree(cache_dir, ignore_errors=True)

# (If you want to use the font by directly referencing the file path)
# from matplotlib.font_manager import FontProperties
# georgia_font = FontProperties(fname='/path/to/georgia.ttf')

# Set Georgia as the default font family
plt.rcParams['font.family'] = 'Georgia'

# Create a sample plot
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]
plt.plot(x, y)

# Add title and labels
plt.title('Plot with Georgia Font')
plt.xlabel('X-axis Label')
plt.ylabel('Y-axis Label')

plt.show()