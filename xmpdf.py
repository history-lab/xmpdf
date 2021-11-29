import pgparse
import pdftotext
import magic
import csv

NO_FILE_ID_FLAG = -999


class Xmpdf:

    def __init__(self, pdf_filename, file_id=NO_FILE_ID_FLAG):
        self.file_id = file_id
        self.filename = pdf_filename
        self.filetype = None
        self.pgcnt = 0
        self.emails = []
        self.error = None
        # convert to text
        try:
            self.filetype = magic.from_file(self.filename)
            self.__pdf2txt()
            self.__parse()
        except Exception as e:
            self.error = str(e)

    def __parse(self):
        i = 0
        current_email = None
        while i < self.pgcnt:
            page = pgparse.parse(self.pdf[i])
            i += 1
            if isinstance(page, pgparse.Email):
                if current_email:
                    self.emails.append(current_email)
                current_email = page
                current_email.pdf_filename = self.filename
                current_email.page_number = i
                current_email.page_count = 1
            elif (isinstance(page, pgparse.Page) and current_email):
                current_email.body += page.body
                current_email.page_count += 1
        if current_email:   # write last email
            self.emails.append(current_email)

    def __pdf2txt(self):
        with open(self.filename, 'rb') as f:
            self.pdf = pdftotext.PDF(f)
            self.pgcnt = len(self.pdf)

    def get_summary(self):
        if self.file_id == NO_FILE_ID_FLAG:
            file_id_str = ''
        else:
            file_id_str = str(self.file_id) + ') '
        if self.error:
            error_str = ', ' + self.error
        else:
            error_str = ''
        return f'{file_id_str}{self.filename}: {self.filetype}; ' \
               f'{self.pgcnt} pages, {len(self.emails)} emails {error_str}'

    def write_csv(self, csv_file):
        email_fields = ['page number', 'page count', 'subject', 'date', 'from',
                        'to', 'cc', 'bcc', 'attachments', 'importance', 'url',
                        'body', 'hdr begin', 'hdr end', 'unprocessed']
        if self.emails:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)

            csv_writer.writerow(email_fields)
            for e in self.emails:
                csv_writer.writerow(e.flatten())