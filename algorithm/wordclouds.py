import wordcloud as wc


# take relative word frequencies into account, lower max_font_size
wordcloud = wc.WordCloud(max_font_size=40, relative_scaling=.5).generate(' '.join(unstopped))
plt.figure()
plt.imshow(wordcloud)
plt.axis("off")
plt.show()



# take relative word frequencies into account, lower max_font_size
wordcloud = wc.WordCloud(max_font_size=30, relative_scaling=0.5, stopwords=wc.STOPWORDS).generate(' '.join(unstopped_nopunctuation))
fig, ax = plt.subplots()
ax.imshow(wordcloud)
ax.set_axis_off()
plt.show()



wordcloud = wc.WordCloud(relative_scaling=0.5, font_path='/Library/Fonts/Chalkduster',width=2000, height=2000).generate(' '.join(stems))
fig, ax = plt.subplots(figsize=(20,10))
ax.imshow(wordcloud)
ax.set_axis_off()
plt.show()

