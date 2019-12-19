## Trbabs

TR BA/BS form for monthly VAT analysis

Description
BA/BS forms submitted monthly between companies are the basis for annual VAT reconciliation

Purchase and Sales Invoices are checked for defined periods for Suppliers and Customers

Using tax_id as key, the Suppliers and Customers are consolidated onto a single BA BS Form doctype

The user may check and send the document as pdf attachment via e-mail defined in the relevant party's Address or Contact data

Form sent date is recorded per BA BS Form

Known Issues
please report any issues you encounter
Installation
Go to your folder containing bench and run:

bench get-app https://github.com/Framras/trbabs.git

At the same prompt run:

bench --site [your_site_name] install-app trbabs

Update
Go to the app folder and run:

git pull https://github.com/Framras/trbabs.git

Go to your folder containing bench and run:

bench build

bench migrate

#### License

MIT
