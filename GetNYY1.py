from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt

georgia_font = FontProperties(fname='/usr/share/fonts/truetype/msttcorefonts/Georgia.tff') # Replace with the actual path

x = [1, 2, 3]
y = [4, 5, 6]

plt.plot(x, y)
plt.xlabel('X-axis', fontproperties=georgia_font)
plt.ylabel('Y-axis', fontproperties=georgia_font)
plt.title('Plot with Georgia Font', fontproperties=georgia_font)

plt.show()