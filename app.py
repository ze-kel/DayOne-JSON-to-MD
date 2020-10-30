import io
import json
import os
import glob

files = glob.glob('./out/*')
for f in files:
    os.remove(f)



readFrom = "2020-10-20-2020.json"



def cleanup(input):
    def quickreplace(a,b):
        nonlocal input
        input = input.replace(a,b)
    quickreplace("\.", ".")
    quickreplace("\)", ")")
    quickreplace("\(", "(")
    quickreplace(r"\\", r"\\"[:-1])
    quickreplace("\+", "+")
    quickreplace("\!", "!")
    quickreplace("\-", "-")
    return input

def cleanFilename(input):
    def quickreplace(a,b):
        nonlocal input
        input = input.replace(a,b)

    quickreplace('"', "")
    quickreplace("*", "")
    quickreplace(r"\\", "")
    quickreplace(r"/", "")
    quickreplace("<", "")
    quickreplace(">", "")
    quickreplace(":", "")
    quickreplace("|", "")
    quickreplace("?","")

    return input


with io.open(readFrom, encoding='utf-8') as read_file:
    data = json.load(read_file)


for entry in data['entries']:
    text = entry['text'].replace("\.", ",").replace("\)", ")").replace("\(", "(").replace(r"\\", r"\\"[:-1])

    date = entry['creationDate'][:-4].replace("-", ".").replace(":", "-").replace("T", " ")


    if text.split("\n")[0][0] is "#":
        title = text.split("\n")[0].replace("# ", "").replace("#", "")
    else:
        title = ""

    rawtags = entry.get('tags')

    
    if rawtags:
        filteredtags = []
        for tag in rawtags:
            if "#"+ tag not in text:
                filteredtags.append(tag)
        tags = "#" + " #".join(filteredtags) + "\n"

    
    text = cleanup(text)
    title = cleanup(title)
    title = cleanFilename(title)


    newfile = io.open("./out/" + date +" — " + title + ".md" , mode="a", encoding="utf-8")
    if rawtags:
        newfile.write(tags)
    newfile.write(text)