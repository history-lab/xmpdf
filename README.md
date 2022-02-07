# xmpdf
Extracts email metadata and text body from a PDF containing emails.

## Installation

    pip install xmpdf

## Usage

    from xmpdf import Xmpdf
    ems = Xmpdf(pdf_file)
    # print summary info about emails in PDF file
    print(ems.info())
    # process emails
    for m in ems.emails:
        process(m)

## Notes
* The initial development of this package was funded in part by The Mellon Foundation’s “Email Archives: Building Capacity and Community” program.
