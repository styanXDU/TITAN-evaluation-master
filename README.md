# TITAN

Multi-Domain Task-oriened dialogue dataset with mixed-initiative interactions.

## Dataset 
We rewrite conversations derived from MultiWOZ2.1 dialog datasets artificially to combine proactive utterance from system side and redesign system dialog act as follows:  

**Request-Select** (ask to select between certain choices)  
System:I have 2 listings one for pizza express and pizza express Fen Ditton. One of these sound good to you?  
User: I would like to know about pizza express  
**Request-Specify** (ask broadly to narrow down quickly)  
System: What price range were you thinking?  
User: No particular price range, but I would like it to be a 4 star hotel.  
**Request-Verify**  (clarify for an ambiguous request)  
User: Can you also help me find a place in town?  
System: To be clarified, are you referring to a place to stay like a hotel?  
User: Yes, please. That is exactly what I need.  
**Request-CrossDomain**  (offer cross-domain service)  
System: I have you booked at mahal of Cambridge…Do you need a taxi between the two places?  
User: Yes, I would like to get to the kohinoor restaurant by the booked time of 19:45.  
**Inform-Specific** (provide answer asked explicitly)  	
System: You may want to try castle galleries  
User: What is their address?  
System: The Castle Galleries is located at Unit SU43, Grande Arcade, Saint Andrews Street.  
**Inform-Addition** (provide implicit answer not requested)	   
User: I'm looking to play a variety of sports.   
System: Sure, there is one such facility, The Cherry Hinton Village Centre, located at colville road, cherry hinton in the east side of town.  
**NoOffer-Relevant**  (provide relevant alternative choices)  
User: Can help me find a restaurant that serves Belgian food in the centre?  
System: I'm sorry, we don't have any Belgian restaurants. Would you like to try a different type? We have African food in the center.  
User: African food is fine.
## Evaluation
We follow the evaluation method proposed in "Shades of {BLEU}, Flavours of Success: The Case of {M}ulti{WOZ}".   
Preprocessed files for TITAN is presented at TITAN-Evaluation-maste\titan_eval\data
### Requierment
python 3.6  
fuzzywuzzy  
lexical-diversity  
python-Levenshtein  
sacrebleu  
sacremoses  
### Usage  
```sh
python evaluate.py [--bleu] [--success] [--richness] --input INPUT.json [--output OUTPUT.json]  
```
#### Input format:

``` python
{
    "xxx0000" : [
        {
            "response": "Your generated delexicalized response.",
            "state": {
                "restaurant" : {
                    "food" : "eatable"
                }, ...
            }, 
            "active_domains": ["restaurant"]
        }, ...
    ], ...
}
```


:thought_balloon: References
```
@inproceedings{nekvinda-dusek-2021-shades,
    title = "Shades of {BLEU}, Flavours of Success: The Case of {M}ulti{WOZ}",
    author = "Nekvinda, Tom{\'a}{\v{s}} and Du{\v{s}}ek, Ond{\v{r}}ej",
    booktitle = "Proceedings of the 1st Workshop on Natural Language Generation, Evaluation, and Metrics (GEM 2021)",
    month = aug,
    year = "2021",
    address = "Online",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2021.gem-1.4",
    doi = "10.18653/v1/2021.gem-1.4",
    pages = "34--46"
}

@inproceedings{budzianowski2018large,
    Author = {Budzianowski, Pawe{\l} and Wen, Tsung-Hsien and Tseng, Bo-Hsiang  and Casanueva, I{\~n}igo and Ultes Stefan and Ramadan Osman and Ga{\v{s}}i\'c, Milica},
    title={MultiWOZ - A Large-Scale Multi-Domain Wizard-of-Oz Dataset for Task-Oriented Dialogue Modelling},
    booktitle={Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing (EMNLP)},
    year={2018}
}

```
## Ackowledgement
We sincerely appreciate for the contributuion of the annotators that involved in TITAN annotation process. We also thank Budzianowski and their team for the creation and release for MultiWOZ dataset that provide a large-scale dialogue corpus for TITAN reorganization. The evaluation method we used for mixed-initiative stratiges is referenced from Nekvinda and their reserach groop.






