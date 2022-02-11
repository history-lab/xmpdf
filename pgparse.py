"""pgparse.py: Classes and function for parsing emails on a PDF page."""
from dataclasses import dataclass, field
from typing import ClassVar
from collections import defaultdict


@dataclass
class Header:
    """A data class for an email header."""

    from_email:     str = None
    to:             list[str] = field(default_factory=list)
    subject:        str = None
    date:           str = None
    cc:             list[str] = field(default_factory=list)
    bcc:            list[str] = field(default_factory=list)
    attachments:    list[str] = field(default_factory=list)
    importance:     str = None
    begin_ln:       int = 0   # start line number
    end_ln:         int = 0   # finish line number
    unprocessed:    list[str] = field(default_factory=list)


@dataclass
class Page:
    """A data class for a PDF page without an email header."""

    body:           str


@dataclass
class Email(Page):
    """A data class for an email."""

    header:         Header
    pdf_filename:   str = field(default_factory=str)
    page_number:    int = field(default_factory=int)
    page_count:     int = field(default_factory=int)
    csv_header:     ClassVar[list] = [
                'pdf file', 'page number', 'page count',
                'subject', 'date',
                'from', 'to', 'cc',
                'bcc', 'attachments',
                'importance', 'body',
                'hdr begin', 'hdr end',
                'unprocessed']

    def flatten(self):
        """Return flattened representation of email header."""
        return [self.pdf_filename, self.page_number, self.page_count,
                self.header.subject, self.header.date,
                self.header.from_email, self.header.to, self.header.cc,
                self.header.bcc, self.header.attachments,
                self.header.importance, self.body,
                self.header.begin_ln, self.header.end_ln,
                self.header.unprocessed]

    def info(self):
        """Return email header info summary."""
        summary = f'{self.page_number}, {self.page_count}; ' \
                  f'{self.header.subject}; {self.header.date}; ' \
                  f'{self.header.from_email}; {self.header.to}'
        return summary


@dataclass
class HeaderParser:
    """A class that parses an email header on a page, if it exists."""

    pgarr:          list[str]
    _FIELD_TOKENS:  ClassVar[list[str]] = ['from', 'to', 'cc', 'bcc',
                                           'subject', 'date', 'sent',
                                           'importance', 'attachments']
    _MAX_START_LN:     ClassVar[int] = 12        # max start line for header
    _MAX_COL_COLON: ClassVar[int] = 14        # rt most column for header colon
    _header:        defaultdict(str) = field(
        default_factory=lambda: defaultdict(str))
    _ln:            int = 0                           # line position in page
    _token:         str = field(default_factory=str)  # last field token
    _lncnt:         int = 0                           # len(pgarr)

    def _get_token(self, str):
        # fix erroneous OCR spaces
        return str.lower().replace(' ', '')

    def _find_start(self):
        self._ln = 0
        while True:
            if self._ln == self._MAX_START_LN:  # reached _MAX_START_LN
                return False
            if self._ln == self._lncnt:         # reached end of page
                return False
            loc = self.pgarr[self._ln][:self._MAX_COL_COLON].find(':')
            if loc != -1:
                self._token = self._get_token(self.pgarr[self._ln][:loc])
                if self._token in self._FIELD_TOKENS:
                    self._header['begin_ln'] = self._ln + 1  # human counting
                    return True     # Found the start of header
            self._ln += 1

    def _tokenize(self):
        """Tokenize a string if it represents an email header element."""
        line = self.pgarr[self._ln].strip()
        loc = line.find(':')
        if loc != -1:           # found add to header dictionary
            # self._token = line[:loc].lower().replace(' ', '')
            self._token = self._get_token(line[:loc])
            if self._token in self._FIELD_TOKENS:
                self._header[self._token] = line[loc+1:].strip()
            else:
                if self._header['unprocessed']:
                    self._header['unproccessed'] = \
                     self._header['unprocessed'].append(line)
                else:
                    self._header['unprocessed'] = [line]
                # print(f'Warning - unprocessed header element: {self._token}')
                # print(line)
        elif self._token in self._FIELD_TOKENS:
            # existing token value carried onto next line
            self._header[self._token] += line

    def _next_line(self):
        """Return True if there is another line in the header else False."""
        # Side effect: always increments ln."""
        self._ln += 1
        if self._ln >= self._lncnt:                # Reached end of page
            return False
        elif self.pgarr[self._ln].strip() == '':   # Blank line indicates EOH
            return False
        else:
            return True

    def _convert_obj(self):
        """Create a Header object based on the self._header dictionary.

        If required fields are missing, raise warnings and return None.
        """
        if not self._header['date']:
            self._header['date'] = self._header.get('sent')
        if self._header['date'] and self._header['from']:
            return Header(from_email=self._header.get('from'),
                          to=self._header.get('to'),
                          cc=self._header.get('cc'),
                          bcc=self._header.get('bcc'),
                          subject=self._header.get('subject'),
                          date=self._header.get('date'),
                          attachments=self._header.get('attachments'),
                          importance=self._header.get('importance'),
                          begin_ln=self._header.get('begin_ln'),
                          end_ln=self._header.get('end_ln'),
                          unprocessed=self._header.get('unprocessed'))
        else:  # No date: or from:, v likely a false positive header
            return None

    def parse(self):
        """Parse the email header if it exists."""
        self._lncnt = len(self.pgarr)         # lines in page
        if self._find_start():                # find the start of the header
            while True:                       # while in header
                self._tokenize()              # process header line
                if not self._next_line():     # end of header
                    break
            self._header['end_ln'] = self._ln
            header_obj = self._convert_obj()  # convert _header to object
            return header_obj
        else:                                 # no header
            return None


def parse(page):
    """Parse a string representation of a PDF page.

    Returns either a Page or an Email object depending on whether the page has
    an email header.
    """
    pgarr = page.splitlines()
    hp = HeaderParser(pgarr)
    header = hp.parse()
    if header:
        # ignore blank lines between email header and text
        body_begin = header.end_ln
        for ln in pgarr[header.end_ln::]:
            if ln == '':
                body_begin += 1
            else:
                break
        body = '\n'.join(pgarr[body_begin::])
        return Email(header=header, body=body)
    else:
        body = '\n'.join(pgarr)
        return Page(body=body)


def main():
    """Run as script for testing purposes."""
    example_page = """
    From:       yogi.bear@cartoon.com
    To:         booboo.bear@cartoon.com
    Subject:    this afternoon
    Date:       Thursday, March 25, 2021 06:16:10 AM
    Status:     Urgent

    Hi Booboo:

    Let's go see the ranger this afternoon at 2 o'clock, ok?

    Yogi
    """
    pg = parse(example_page)
    print(type(pg))
    print(pg)
    example_page = """
    Up next:

    This is an example of a continuation page, which occurs when an email
    extends beyond a page.

    Thanks,
    Yogi
    """
    pg = parse(example_page)
    print(type(pg))
    print(pg)

    exit()
    e1 = Email(header=Header(from_email='yogi.bear@cartoon.com',
                             to=['booboo.bear@cartoon.com'],
                             subject='this afternoon',
                             date='Thursday, March 25, 2021 06:16:10 AM'),
               body="""Hi Booboo:

               Let's go see the ranger this afternoon at 2 o'clock, ok?

               Yogi""")
    print(e1)


if __name__ == "__main__":
    main()
