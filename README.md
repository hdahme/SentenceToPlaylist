# Spotify Sentences
A simple Python script that turns sentences into playlists using Spotify's API

Running the Code:
-----------------
```
python SentenceToPlaylist.py This program does not have buddha nature
>>> 
========================================================================
Coverage:  95.0 %
------------------------------------------------------------------------
Title                 Artist        Album                               Spotify Link
This                  Ed Sheeran    +                                   spotify:track:0pJfsPQesJyCnR5XWZyvj9
Program               Noisia        Program / Regurgitate               spotify:track:50I96zVpp2sH1F560VPHIZ
Does Not Compute      Cameron       Cameron's Meditation - Calm Down    spotify:track:4T1SbwJQdtcyr1N7awtans
Have Faith            CYPHR         Sound Pellegrino Presents SND.PE    spotify:track:6WH5c8uojm4L2mcOUlE5rq
Buddha Nature         Deuter        Buddha Nature                       spotify:track:2s0kXrSdexAw2GHkQeSvOi
```

Implementation:
---------------
This problem can be effectively seen as a pathfinding problem, where the goal is the playlist with the highest coverage of words, but also the fewest songs in it. This code turns the input sentence into possible start states, and then performs a weighted breadth first / A* search. Preference is given to states or paths with longer titles, and which more closely match the input phrase.

Limitations:
------------
- Well... obviously searching every phrase we come across is not optimal by any means. To remedy this performance hit, caching could be implemented - or even better yet, a local data store of all songs on Spotify.
