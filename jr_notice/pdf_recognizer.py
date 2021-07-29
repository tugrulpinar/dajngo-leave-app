from pdfminer.high_level import extract_text


class PdfRecognizer:
    def __init__(self, file):
        self.applicant_names = None
        self.applicant_lastnames = None
        self.number_of_applicants = None
        self.application_type = None
        self.decision_maker = None
        self.file = file
        self.app_fullname = None
        self.errors = []

    def scan(self):
        self.extract_fullnames()
        self.extract_application_type()

    def extract_fullnames(self):
        try:
            # EXTRACT THE TEXT OUT OF THE PDF FILE
            text = extract_text(self.file, page_numbers=[0])
            # print(text)

            # GET THE SECTION WE WANT - THE UPPER PART
            section = text.split("and")[0]
            chunks = set(section.split('\n'))
            # print(chunks)

            chunks_stripped = set(map(lambda x: x.strip(), chunks))

            # DEFINE THE WORDS THAT YOU WANT TO REMOVE
            redundants = {
                "Registry",
                "FEDERAL",
                "FEDERAL COURT",
                "Registry No: IMM-",
                "B E T W E E N",
                "B E T W E E N :",
                "Applicant",
                "Applicants",
                "BETWEEN",
                "Between",
                "Between:",
                "Court",
                "Court File No.",
                "MINISTER",
                "-",
                ""
            }

            difference = chunks_stripped.difference(redundants)

            # print(f"\n{len(difference)} Applicant(s) in total.\n")
            self.number_of_applicants = len(difference)

            self.applicant_lastnames = [applicant.split(
                " ")[-1] for applicant in difference]

            self.applicant_names = [" ".join(applicant.split(
                " ")[:-1]) for applicant in difference]

            self.app_fullname = tuple(
                zip(self.applicant_names, self.applicant_lastnames))

        except:
            first_error_text = "Sorry, I can not recognize the text in the first page of the file."
            print(first_error_text)
            self.errors.append(first_error_text)

    def extract_application_type(self):
        try:
            text = extract_text(self.file, page_numbers=[1])
            if "Appeal" in text:
                self.application_type = "RAD"
                self.decision_maker = "Immigration and Refugee Board - IRB"
            elif "Protection Division" in text:
                self.application_type = "RPD"
                self.decision_maker = "Immigration and Refugee Board - IRB"
            elif "PRRA" in text:
                self.application_type = "PRRA"
                self.decision_maker = "Canada Border Services Agency - CBSA"
            elif "H&C" in text:
                self.application_type = "H&C"
                self.decision_maker = "Immigration, Refugees and Citizenship Canada - IRCC"
        except:
            second_error_text = "Sorry, I can not recognize the text in the second page of the file."
            print(second_error_text)
            self.errors.append(second_error_text)
