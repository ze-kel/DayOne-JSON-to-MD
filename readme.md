Simple app that converts jsons(packed with media files into zip) exports from [Day One](https://dayoneapp.com/) to Markdown.

I wrote it to export all my entries to [Obsidian](https://obsidian.md/). By default it uses Obsidian's ```![[]]``` linking, change relativeMediaLinking value inside to False.

I haven't tested it for anything other than exporting text, headers, tags, date, photos and audios. 


How to use:
0. Install python 3
1. Go to Dayone Export and click "Export Day One JSON". You can export everything to one zip file or have separate ones.
2. Download app.py
3. Create "in" folder in the same directory as app.py and place all zips you have there
4. Run ```python app.py```