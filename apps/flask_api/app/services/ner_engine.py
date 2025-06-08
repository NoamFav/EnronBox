import spacy
import re
from app.services.db import store_entities

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

        return {"names": names, "orgs": orgs, "dates": dates}

    def anonymize_data(self, body: str) -> str:
        """
        Anonymize personal data with placeholders.
        """
        entities = self.extract_entities(body)

        for name in entities["names"]:
            body = re.sub(rf"\b{name}\b", "[NAME]", body)

        for org in entities["orgs"]:
            body = re.sub(rf"\b{org}\b", "[ORG]", body)

        for date in entities["dates"]:
            body = re.sub(rf"\b{date}\b", "[DATE]", body)

        return body
    
    def save_entities_to_db(self, email_id: str, body: str):
        """
        Extract entities from the email body and store them in the database.

        Args:
            email_id (str): The ID of the email.
            body (str): The body of the email.
        """
        entities = self.extract_entities(body)
        store_entities(email_id, entities)
