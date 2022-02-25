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

## OS Dependencies
If you encounter errors installing xmpdf, please check the OS-level
dependencies of the [pdftotext](https://pypi.org/project/pdftotext/)
package to ensure you have the required libraries installed, as xmpdf utilizes
this package.

## Notes
* Assumes an email ends when a new email begins
* Works best with a standard email header (i.e., From:, To:, Sent:, Subject:)
* The initial development of this package was funded in part by The Mellon Foundation’s “Email Archives: Building Capacity and Community” program.
