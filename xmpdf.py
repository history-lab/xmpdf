"""xmpdf.py: Xmpdf class definition."""
import pdftotext
import csv
import jsonpickle
from pgparse import parse, Email, Page


class Xmpdf:
    """
    A class that parses the emails in a PDF.

    ...
    Attributes
    ----------
    file : obj
        file or file-like object containing emails
    pgcnt : int
        number of pages in file_id
    emails : list
        email objects
    error : str
        errors encountered during processing

    Methods
    -------
    info()
        Returns high-level descriptive information about the PDF file
    to_json()
        Returns jsonified representation of Xmpdf object
    to_csv(csv_filename)
        Writes a CSV representation of the Xmpdf emails to csv_filename
    """

    def __init__(self, pdf_file):
        """
        Create Xmpdf object.

        Takes a PDF file and creates an Xmpdf instance which holds a parsed
        representation of the emails in the PDF in a dictionary.
        """
        self.pgcnt = 0
        self.emails = []
        self.error = None
        # convert to text
        try:
            self.pdf = pdftotext.PDF(pdf_file, physical=True)
            self.pgcnt = len(self.pdf)
            self.__parse()
        except Exception as e:
            self.error = str(e)

    def __parse(self):
        i = 0
        current_email = None
        while i < self.pgcnt:
            page = parse(self.pdf[i])
            i += 1
            if isinstance(page, Email):
                if current_email:
                    self.emails.append(current_email)
                current_email = page
                current_email.page_number = i
                current_email.page_count = 1
            elif (isinstance(page, Page) and current_email):
                current_email.body += page.body
                current_email.page_count += 1
        if current_email:   # write last email
            self.emails.append(current_email)

    def info(self):
        """Return high-level descriptive information about the PDF file."""
        if self.error:
            error_str = ', ' + self.error
        else:
            error_str = ''
        return f'{self.pgcnt} pages, {len(self.emails)} emails {error_str}'

    def email_metadata(self):
        """Return key metadata elements for each email in the PDF."""
        em_meta = []
        for e in self.emails:
            em_meta.append(e.info())
        return(em_meta)

    def to_json(self):
        """Return jsonified representation of Xmpdf object."""
        return jsonpickle.encode(self, unpicklable=False, indent=4)

    def to_csv(self, csv_file):
        """Write CSV representation of Xmpdf emails."""
        if self.emails:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(self.emails[0].csv_header)
            for e in self.emails:
                csv_writer.writerow(e.flatten())
