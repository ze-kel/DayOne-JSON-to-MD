import io
import json
import os
import glob
import zipfile
import fnmatch
import shutil
import sys




# If you use Obsidian.md you don't have to specifically point to media file as long as they are somewhere in "embedded media" folder. 
# If true link will be ![[file]] else ![](/folder/file)
relativeMediaLinking = True


# Cleans up text from "\special character"
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

# Removes everything that can't be in file name
def cleanFilename(input):
    def quickreplace(a,b):
        nonlocal input
        input = input.replace(a,b)

    quickreplace('"', "")
    quickreplace("*", "")
    quickreplace("\\", " ")
    quickreplace(r"/", " ")
    quickreplace("<", "")
    quickreplace(">", "")
    quickreplace(":", "")
    quickreplace("|", " ")
    quickreplace("?","")
    quickreplace(".", "")

    return input


def processJson(readFrom, subfolder, tempsubfolder, outpath):

    # Open Json Load as Dict
    with io.open(readFrom, encoding='utf-8') as read_file:
        data = json.load(read_file)
    
    # Setting and creating output folder for out zip
    folderpath = outpath + "/" + subfolder + "/"
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
    
    if not os.path.exists(folderpath + "/audios/"):
        os.makedirs(folderpath + "/audios/")
    if not os.path.exists(folderpath + "/photos/"):
        os.makedirs(folderpath + "/photos/")


    # Loop over entries
    for entry in data['entries']:
        
        # Get raw text
        text = entry['text']


        # Getting date looking like "2020-01-01T09:03:48Z" and formating it as "2020.01.01 09-44"
        date = entry['creationDate'][:-4].replace("-", ".").replace(":", "-").replace("T", " ")


        # If first line starts with "# " — post has a title
        if text.split("\n")[0][:2] == "# ":
            title = text.split("\n")[0].replace("# ", "").replace("#", "")
        else:
            title = ""

        
        # Process all "dayone-momnts"(photos and audios)
        splitted = text.split("\n")
        filtered = fnmatch.filter(splitted, '![](dayone-moment:*)')

        for moment in filtered:
            # ![](dayone-moment:\/\/F7EEC3394BC0455FA513D9CAA0557C7E) => F7EEC3394BC0455FA513D9CAA0557C7E) = > F7EEC3394BC0455FA513D9CAA0557C7E
            momentIdentifier = moment.split("/")[-1]
            momentIdentifier = momentIdentifier[:-1]

            # Iterate over all media attached to entry and find filename and format of the right one
            if "audio" in moment:
                momentIn = entry['audios']
                folder = 'audios'
            else:
                momentIn = entry['photos']
                folder = 'photos'
            for momentItem in momentIn:
                if momentIdentifier == momentItem['identifier']:
                    if "type" in momentItem:
                        momentFormat = momentItem['type']
                    else:
                        momentFormat = momentItem['format']
                        # For some reason format is codec not container — "aac" corresponds to "m4a" files. This is a stupid fix but still.
                        if momentFormat == "aac":
                            momentFormat = "m4a"

                    # Jpegs has filenames. Audios don't
                    if 'filename' in momentItem:
                        # Filename is IMG_000.HEIC, we don't need codec
                        newName = momentItem['filename'].split('.')[0]
                    else:
                        newName = momentItem['date'][:-4].replace("-", ".").replace(":", "-").replace("T", " ")


                    momentFile = momentItem['md5']
            
            #Copy and rename file
            shutil.copy2(f'temp/{tempsubfolder}/{folder}/{momentFile}.{momentFormat}', f'./out/{subfolder}/{folder}/{newName}.{momentFormat}')


            
            if relativeMediaLinking:
                text = text.replace(moment, f"![[{newName}.{momentFormat}]]")
            else:
                text = text.replace(moment, f"![](/{folder}/{newName}.{momentFormat})")
            
        # Get all tags from json
        rawtags = entry.get('tags')
        # Sometimes tags are set withing the text — then we don't need to append them to text
        writetags = False
        if rawtags:
            filteredtags = []
            for tag in rawtags:
                if "#"+ tag not in text:
                    filteredtags.append(tag.replace(" ", ""))
            if len(filteredtags)>0:
                tagsString = "#" + " #".join(filteredtags) + "\n"
                writetags = True

        # Cleaning Stuff
        text = cleanup(text)
        title = cleanup(title)
        title = cleanFilename(title)

        # Setting filename from date and title and writing it into subfolder in "out folder" with a name corresponding to .zip name
        newfilename = date +" — " + title + ".md" 
        newfile = io.open(folderpath  +  "/" + newfilename , mode="a", encoding="utf-8")
        if writetags:
            newfile.write(tagsString)
        newfile.write(text)


def ProcessZips(inpath, outpath):
    for zipname in os.listdir(inpath + "/"):
        if zipname.endswith(".zip"):
            zipnameClean = zipname.split(".")[0]
            with zipfile.ZipFile( inpath + "/" + zipname, 'r') as zip_ref:
                
                zip_ref.extractall("temp/" + zipnameClean)

            for jsonname in os.listdir("temp/" + zipnameClean):
                jsonnameClean = jsonname.split(".")[0]
                if jsonname.endswith(".json"):
                    processJson("temp/" + zipnameClean + "/" + jsonname  ,jsonnameClean, zipnameClean, outpath)
    shutil.rmtree('temp')




if __name__ == "__main__":
    inpath = "in"
    outpath = "out"
    ProcessZips(inpath, outpath)
    print(f"Finished, check {outpath} folder")

