import spacy

nlp = spacy.load("en_core_web_sm")

class Extractor:
    def extract_entities(self, body: str) -> dict:
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