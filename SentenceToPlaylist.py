import sys, string, httplib, json, re

''' The idea here is to explore the space of song title nodes in an A* 
 manner, exploring promising leads first. Promising means the program will
 give preference to longer titles, which closely match the input phrases
 
 call this program with 
 python Spotify.py These words constitute the poem
'''

class Song:
    # an object to hold the data associated with a song title
    def __init__(self, title, artist, album, link):
        self.title = title
        self.artist = artist[0]['name']
        self.album = album['name']
        self.link = link
    
    def __str__(self):
        return self.title + '\t\t' + self.artist[0]['name'] + '\t\t' + \
               self.album['name'] + '\t\t' + self.link

class Path:
    # - pathSoFar is a collection of Songs thus far formed
    # - remainder is the remaining words which need to be matched
    # - coverage is how closely pathSoFar covers the words (excluding the 
    # remainder) in the poem. Measured in edit distance 
    def __init__(self, pathSoFar, remainder, coverage):
        self.pathSoFar = pathSoFar
        self.remainder = remainder
        self.coverage = coverage
        
# Lifted from Wikipedia, useful for fuzzy matching query terms to get strings 
# which approximate the requested phrase. Modified to work on words, vs spaces
def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    
    s1 = s1.split()
    s2 = s2.split()
    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)
 
    previous_row = xrange(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
 
    return previous_row[-1]*1.0

# Break a string into all possible segments, starting from the first word
def breakStr(s):
    pieces = []

    s = s.split()
    for i in range(len(s)):
        pieces.append(' '.join(s[0:i+1]))

    # Could do some semantic analysis, as most song names will probably be 
    # sentences, noun phrases or verb phrases, but that could get expensive
    return pieces

# Search the Spotify web library for the phrase, examine the first page of matches
# to determine if there's a valid match. If there is, return the closes match, 
# otherwise return None.
def search(phrase):
    conn = httplib.HTTPConnection("ws.spotify.com")
    conn.request("GET", "/search/1/track.json?q="+str(phrase.replace(' ', '%20')))
    res = conn.getresponse()
    res = json.loads(res.read())
    numResponse = min(res['info']['num_results'], res['info']['limit'])
    res = res['tracks']
    
    closestMatch = (float("inf"), None)
    
    # Obvious optimization, don't evaluate all results, or use length heuristics
    # to throw out non-promising titles before evaluation
    for i in range(min(len(res), numResponse)):
        editDistance = levenshtein(re.sub(r'[^\w\s]', "", res[i]['name']).lower(), phrase)
        if editDistance < closestMatch[0]:
            closestMatch = (editDistance, Song(res[i]['name'], res[i]['artists'], \
                                    res[i]['album'], res[i]['href']))
        if editDistance == 0:
            return closestMatch
            
    return closestMatch

# Returns the index of where to insert on the frontier. A very obvious 
# optimization is to use binary search to find the index to insert the path as
# opposed to a linear search for the frontier.
# Returns the first index where the coverage decreases, thereby preserving order
def insertIndex(f, d):
    for i in range(len(f)):
        if d < f[i].coverage:
            return i
    return -1

# The entry point
inSentence = ' '.join(sys.argv[1:])
inSentence = re.sub(r'[^\w\s]', "", inSentence).lower()

if not inSentence:
    print 'Please pass a sentence as an argument'
    exit(1)

# The paths to explore. The sentence fragments are appended in reverse order, so
# longer names are preferred. It's also sorted by edit distance, so more 
# accurate/covering names are preferred
frontier = []
inS = breakStr(inSentence)
inS.reverse()

# Set up the frontier, by creating Path objects for all segments in the input
for sen in inS:
    s = search(sen) 
    if s[1] is not None:
        remainder = string.replace(inSentence, sen, '', 1).strip()
        frontier.insert(insertIndex(frontier, s[0]), Path([s[1]], remainder, s[0]))
        
# Iterate through the frontier until we have a path which covers all of the 
# desired words
while len(frontier[0].remainder) > 0:
    head = frontier.pop(0)
    inS = breakStr(head.remainder)
    inS.reverse()
    for sen in inS:
        s = search(sen) 
        if s[1] is not None:
            # since append modifies the input argument
            pathCopy = head.pathSoFar[:]
            pathCopy.append(s[1])
            
            remainder = string.replace(head.remainder, sen, '', 1).strip()
            
            frontier.insert(insertIndex(frontier, head.coverage + s[0]), \
                            Path(pathCopy, remainder, head.coverage + s[0]))    

# Output the shortest, most matching playlist
f = frontier.pop(0)
print '========================================================================'
print 'Coverage: ', (1.0 - f.coverage/len(inSentence))*100,'%'
print '------------------------------------------------------------------------'

# Purely for formatting a nice table
headers = ['Title', 'Artist', 'Album', 'Spotify Link']
songs = []
for s in f.pathSoFar:
    songs.append([s.title, s.artist, s.album, s.link])
    
print ''.join(column.ljust(50) for column in headers)
for row in songs:
    print ''.join(str(column).ljust(50) for column in row)
