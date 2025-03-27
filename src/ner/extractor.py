import spacy

nlp = spacy.load("en_core_web_sm")

def extract_entities(body: str) -> dict:
    email = nlp(body)

    names = []
    orgs = []
    dates = []

    for ent in email.ents:
        if ent.label_ == "PERSON":
            names.append(ent.text)
        elif ent.label_ == "ORG":
            orgs.append(ent.text)
        elif ent.label_ == "DATE":
            dates.append(ent.text)

    return {
        "names": names,
        "orgs": orgs,
        "dates": dates
    }


#Below is the test function I use to test if NER works. I kept this in case you also want to do some tests. Feel free to delete it.
#Also my test email body below:
#I have scheduled a meeting on January 3rd with Max. Therefore our meeting of Maastricht University Investigation Group would be postponed to the next Friday. Along with an exterior guest Lewis.
#So the outputs are:
#extracted entities: {'names': ['Max', 'Lewis'], 'orgs': ['Maastricht University Investigation Group'], 'dates': ['January 3rd', 'the next Friday']}
def test():
    email = input("paste email here: ")
    entities = extract_entities(email)
    print("extracted entities:", entities)

if __name__ == "__main__":
    test()
