# Brothers Karamazov Novel Graph with ChatGPT

Brothers Karamaozv is a masterpiece by Fyodor Dostoevsky. The complexity of the characters and their interactions made me build a tool with chatGPT to explore and summarize this masterpiece. Enjoy diving into this Novel Graph: [schoobani.github.io/novel-graph-app](https://schoobani.github.io/novel-graph-app)

![Brothers Karamaozv Novel Graph](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Brothers Karamaozv Novel Graph")

---

## How the graph is built?

### Step 1: generate interactions
I provided small chuncks of the novel to chatGPT and asked it to generate characters and their relationships from that chunck in a python object.

prompt:

```
The following is part of the Brothers Karamazov novel:

Adelaïda Ivanovna Miüsov’s action was similarly, no doubt, an echo of other people’s ideas, and was due to the irritation caused by lack of mental freedom. She wanted, perhaps, to show her feminine independence, to override class distinctions and the despotism of her family. And a pliable imagination persuaded her, we must suppose, for a brief moment, that Fyodor Pavlovitch, in spite of his parasitic position, was one of the bold and ironical spirits of that progressive epoch, though he was, in fact, an ill‐natured buffoon and nothing more. What gave the marriage piquancy was that it was preceded by an elopement, and this greatly captivated Adelaïda Ivanovna’s fancy. Fyodor Pavlovitch’s position at the time made him specially eager for any such enterprise, for he was passionately anxious to make a career in one way or another. To attach himself to a good family and obtain a dowry was an alluring prospect. As for mutual love it did not exist apparently, either in the bride or in him, in spite of Adelaïda Ivanovna’s beauty. This was, perhaps, a unique case of the kind in the life of Fyodor Pavlovitch, who was always of a voluptuous temper, and ready to run after any petticoat on the slightest encouragement. She seems to have been the only woman who made no particular appeal to his senses.  Immediately after the elopement Adelaïda Ivanovna discerned in a flash that she had no feeling for her husband but contempt. The marriage accordingly showed itself in its true colors with extraordinary rapidity. Although the family accepted the event pretty quickly and apportioned the runaway bride her dowry, the husband and wife began to lead a most disorderly life, and there were everlasting scenes between them. It was said that the young wife showed incomparably more generosity and dignity than Fyodor Pavlovitch, who, as is now known,\ngot hold of all her money up to twenty‐five thousand roubles as soon as she received it, so that those thousands were lost to her for ever. The little village and the rather fine town house which formed part of her dowry he did his utmost for a long time to transfer to his name, by means of some deed of conveyance. He would probably have succeeded, merely from her moral fatigue and desire to get rid of him, and from the contempt and loathing he aroused by his persistent and shameless importunity. But, fortunately, Adelaïda Ivanovna’s family intervened and circumvented his greediness.

Extract only human characters and persons (not places and other entities) from it and understand relationships between each of two characters.  make sure to generate the results in the following python dictionary format:

{"from": "char1", "to": "char2", "label":"relation"}
```

generated text:

```python
{"from": "Fyodor Pavlovitch", "to": "his wife", "label": "spouse"}
{"from": "Fyodor Pavlovitch", "to": "Mitya", "label": "parent"}
{"from": "Fyodor Pavlovitch", "to": "his wife's family", "label": "in-law"}
{"from": "Fyodor Pavlovitch", "to": "his wife's family", "label": "opponent"}
{"from": "Fyodor Pavlovitch", "to": "his wife", "label": "abandoner"}
```

### Step 2: build graph

ChatGPT was able to generate 3046 interactions between different characters of the novel. Before building the graph I had to:

-  replace all different names used for a character with a single name, for example Alyosha, the protagonist of the novel, is mentioned by more than 12 different names.
-  Conditionaly map names based on their appearance order. for example if "his father" is appearing after "Dmitri", it should be replaced with "Fyodor karamazov".
-  Remove non trivial nodes, for example the node "killer" or "doctor" are too general and can point to many different characters in the novel.

Now I can use `networkx` or any other libraries to build the graph.

### Step 3: generate descriptions

Finaly I asked chatGPT to provide desciptions about each node using the following promopt:

```
write a paragraph about the role of Ivan in the Brothers Karamazov Novel and describe the role Ivan plays in the novel. 
In possible cases, add a deeper analyses of different aspects of the character.
```

I also asked it describe the relationships between each pair of nodes in the graph:

```
In the borthers karamazov novel Ivan and Grushenka are interacting with each other in different ways. 
Describe and analyse the relationship between Ivan and Grushenka.
Make sure to only describe the relationship and don't provide any further details on each character.
```

### Caution 

The graph can have mistakes! In some cases chatGPT can't figure out the relationships among minor characters and sometimes it starts hallucinating and writing unreal descriptions about relationships.