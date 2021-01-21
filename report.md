
ILS data field analysis
=======================

Contents
========

* [ILS data field analysis](#ils-data-field-analysis)
	* [Data overview](#data-overview)
	* [A closer look at the different fields](#a-closer-look-at-the-different-fields)
	* [CLAIMCYCLE](#claimcycle)
	* [VCODE1](#vcode1)
	* [VCODE2](#vcode2)
	* [VCODE3](#vcode3)
	* [ORDERS](#orders)
	* [CLAIMS](#claims)
	* [CANCELS](#cancels)
	* [RECEIPTS](#receipts)
	* [INVOICES](#invoices)
	* [ORD CLMD](#ord-clmd)
	* [CPY RCVD](#cpy-rcvd)
	* [ORD TOT](#ord-tot)
	* [INV TOT](#inv-tot)
	* [EPRICE RCVD](#eprice-rcvd)
	* [EPRICE CNCL](#eprice-cncl)
	* [AVG WEEKS](#avg-weeks)
	* [DISCOUNT](#discount)
	* [VENDOR MSG](#vendor-msg)
	* [LANGUAGE](#language)
	* [GIR CODE](#gir-code)
	* [RECORD #(VENDOR)](#record-vendor)
	* [CREATED(VENDOR)](#createdvendor)
	* [UPDATED(VENDOR)](#updatedvendor)
	* [REVISIONS(VENDOR)](#revisionsvendor)
	* [VENCODE](#vencode)
	* [VENNAME](#venname)
	* [ACCTNUM](#acctnum)
	* [CONTACT](#contact)
	* [ADDRESS1](#address1)
	* [ADDRESS2](#address2)
	* [ALTCODE](#altcode)
	* [PHONE NUM](#phone-num)
	* [EMAIL](#email)
	* [NOTE1](#note1)
	* [NOTE2](#note2)
	* [NOTE3](#note3)
	* [SPECIAL](#special)
	* [FTP INFO](#ftp-info)

# ILS data field analysis


Scroll down to learn about your legacy data.
## Data overview


Your file contains 98 rows (records) and 38 columns (fields). These are the present fields:  
['CLAIMCYCLE' 'VCODE1' 'VCODE2' 'VCODE3' 'ORDERS' 'CLAIMS' 'CANCELS'
 'RECEIPTS' 'INVOICES' 'ORD CLMD' 'CPY RCVD' 'ORD TOT' 'INV TOT'
 'EPRICE RCVD' 'EPRICE CNCL' 'AVG WEEKS' 'DISCOUNT' 'VENDOR MSG'
 'LANGUAGE' 'GIR CODE' 'RECORD #(VENDOR)' 'CREATED(VENDOR)'
 'UPDATED(VENDOR)' 'REVISIONS(VENDOR)' 'VENCODE' 'VENNAME' 'ACCTNUM'
 'CONTACT' 'ADDRESS1' 'ADDRESS2' 'ALTCODE' 'PHONE NUM' 'EMAIL' 'NOTE1'
 'NOTE2' 'NOTE3' 'SPECIAL' 'FTP INFO']
## A closer look at the different fields

## CLAIMCYCLE


-    55
a    13
      4
c     2
b     1
Name: CLAIMCYCLE, dtype: int64  
![Chart](CLAIMCYCLE.svg)
## VCODE1


-    68
      4
Name: VCODE1, dtype: int64  
![Chart](VCODE1.svg)
## VCODE2


-    67
      4
s     1
Name: VCODE2, dtype: int64  
![Chart](VCODE2.svg)
## VCODE3


-    63
e     6
      4
d     2
Name: VCODE3, dtype: int64  
![Chart](VCODE3.svg)
## ORDERS


0       79
1        5
2        1
3        1
1156     1
5        1
6        1
11       1
19       1
26       1
41       1
175      1
61       1
64       1
483      1
116      1
Name: ORDERS, dtype: int64  
![Chart](ORDERS.svg)
## CLAIMS


0      94
3       1
46      1
99      1
119     1
Name: CLAIMS, dtype: int64  
![Chart](CLAIMS.svg)
## CANCELS


0    98
Name: CANCELS, dtype: int64  
![Chart](CANCELS.svg)
## RECEIPTS


0       80
1        4
2        2
3        1
5        1
11       1
20       1
22       1
1057     1
46       1
61       1
64       1
459      1
100      1
243      1
Name: RECEIPTS, dtype: int64  
![Chart](RECEIPTS.svg)
## INVOICES


0       44
1       13
2        8
3        6
9        4
4        3
6        3
5        2
28       1
379      1
235      1
100      1
48       1
1197     1
32       1
16       1
26       1
23       1
17       1
271      1
13       1
7        1
127      1
Name: INVOICES, dtype: int64  
![Chart](INVOICES.svg)
## ORD CLMD


0      94
3       1
46      1
99      1
119     1
Name: ORD CLMD, dtype: int64  
![Chart](ORD_CLMD.svg)
## CPY RCVD


0       80
1        4
2        2
3        1
5        1
11       1
22       1
416      1
36       1
1061     1
46       1
61       1
64       1
459      1
101      1
Name: CPY RCVD, dtype: int64  
![Chart](CPY_RCVD.svg)
## ORD TOT


£0.00         82
£25.00         1
£230.00        1
£969.01        1
£1,319.59      1
£8,936.45      1
£4,361.04      1
£120.00        1
£947.00        1
£81.80         1
£9,734.03      1
£39,823.01     1
£36.00         1
£58.95         1
£850.00        1
£30.50         1
£965.00        1
Name: ORD TOT, dtype: int64  
![Chart](ORD_TOT.svg)
## INV TOT


£0.00         79
£777.42        1
£23.50         1
£1,319.59      1
£14,902.06     1
£655.00        1
£30,592.53     1
£139.30        1
£515.00        1
£1,857.00      1
£380.90        1
£390.54        1
£9,336.08      1
£964.86        1
£122.00        1
£822.50        1
£850.00        1
£475.00        1
£122.95        1
£50.95         1
Name: INV TOT, dtype: int64  
![Chart](INV_TOT.svg)
## EPRICE RCVD


£0.00         83
£989.00        1
£850.00        1
£8,702.25      1
£50.95         1
£81.80         1
£230.00        1
£515.00        1
£30.50         1
£3,825.79      1
£1,836.95      1
£18.00         1
£1,319.59      1
£35,675.20     1
£120.00        1
£12,024.09     1
Name: EPRICE RCVD, dtype: int64  
![Chart](EPRICE_RCVD.svg)
## EPRICE CNCL


£0.00    98
Name: EPRICE CNCL, dtype: int64  
![Chart](EPRICE_CNCL.svg)
## AVG WEEKS


0      90
1       3
3       1
5       1
15      1
23      1
123     1
Name: AVG WEEKS, dtype: int64  
![Chart](AVG_WEEKS.svg)
## DISCOUNT


0     94
10     2
15     1
16     1
Name: DISCOUNT, dtype: int64  
![Chart](DISCOUNT.svg)
## VENDOR MSG


Series([], Name: VENDOR MSG, dtype: int64)
## LANGUAGE


Series([], Name: LANGUAGE, dtype: int64)
## GIR CODE


0    98
Name: GIR CODE, dtype: int64  
![Chart](GIR_CODE.svg)
## RECORD #(VENDOR)


v10000434    1
v10000318    1
v10000884    1
v10000598    1
v10000756    1
            ..
v10000525    1
v10000793    1
v10000914    1
v10000306    1
v10000057    1
Name: RECORD #(VENDOR), Length: 98, dtype: int64  
![Chart](RECORD_#(VENDOR).svg)
## CREATED(VENDOR)


20-07-2004    67
20-11-2020     2
19-10-2020     2
06-11-2020     1
03-07-2018     1
09-09-2008     1
18-11-2020     1
15-01-2007     1
16-11-2006     1
12-10-2006     1
01-12-2006     1
21-03-2006     1
22-01-2007     1
28-04-2008     1
29-05-2007     1
05-02-2007     1
25-08-2009     1
10-12-2007     1
26-11-2007     1
31-07-2006     1
20-05-2008     1
09-07-2007     1
19-03-2009     1
08-01-2009     1
09-10-2008     1
11-10-2004     1
30-01-2009     1
04-08-2014     1
30-04-2007     1
17-10-2007     1
Name: CREATED(VENDOR), dtype: int64  
![Chart](CREATED(VENDOR).svg)
## UPDATED(VENDOR)


20-07-2004    54
16-12-2020     5
17-10-2007     2
11-10-2004     2
19-10-2020     2
12-10-2006     2
06-11-2020     1
19-08-2004     1
19-06-2006     1
09-09-2008     1
21-03-2006     1
01-12-2006     1
15-01-2007     1
16-11-2006     1
18-12-2007     1
19-10-2009     1
06-09-2016     1
18-09-2007     1
08-11-2018     1
28-04-2008     1
25-10-2012     1
29-05-2007     1
05-02-2007     1
10-12-2007     1
27-06-2008     1
25-08-2009     1
18-11-2020     1
26-11-2007     1
09-10-2008     1
20-05-2008     1
09-07-2007     1
20-11-2020     1
30-01-2009     1
06-02-2009     1
04-08-2014     1
05-05-2011     1
14-12-2020     1
Name: UPDATED(VENDOR), dtype: int64  
![Chart](UPDATED(VENDOR).svg)
## REVISIONS(VENDOR)


1     75
2     16
3      3
4      1
5      1
8      1
15     1
Name: REVISIONS(VENDOR), dtype: int64  
![Chart](REVISIONS(VENDOR).svg)
## VENCODE


hb      1
jmls    1
ziii    1
dawp    1
ssf     1
       ..
jh      1
blah    1
ae      1
z3m     1
af      1
Name: VENCODE, Length: 98, dtype: int64  
![Chart](VENCODE.svg)
## VENNAME


Blackwell's Book Services            2
Christopher Edwards                  2
Preservation Equipment Ltd           2
Susanne Schulz-Falster Rare Books    2
Jarndyce                             1
                                    ..
Amazon                               1
Period Bookbinders                   1
Museum Conservation Services Ltd     1
AquaAid (UK) Ltd                     1
A. R. Heath                          1
Name: VENNAME, Length: 94, dtype: int64  
![Chart](VENNAME.svg)
## ACCTNUM


24182200                       1
TCL account number = TRINIT    1
TCL acount number = 1873       1
TRINITY1                       1
808.2145.0                     1
A 9726                         1
TRICOL                         1
1917-10                        1
TCO001                         1
ZP-40355-00                    1
5030670116775                  1
120T100                        1
I6015214                       1
12510617                       1
7229                           1
TRI001                         1
0345520000                     1
T071                           1
                               1
15/513                         1
Name: ACCTNUM, dtype: int64  
![Chart](ACCTNUM.svg)
## CONTACT


Andy Soanes$Sales Account Manager$+44 (0)1865 333144    2
Bob Peel$$                                              1
Michael Laird$$                                         1
Sally Iannacci (sally.iannacci@oup.com)$$               1
Name: CONTACT, dtype: int64  
![Chart](CONTACT.svg)
## ADDRESS1


Beaver House$Hythe Bridge St$Oxford OX1 2ET                                              2
Melford Environmental Services Lts$Melford House, Stevenage Road$                        1
AquaAid Ltd$PO Box 84$                                                                   1
R. G. Watkins$Books and Prints$7 Water Street$Barrington, Ilminster$Somerset TA19 0JR    1
Amanda Hall Rare Books$Home Farmhouse$Teffont Evias, Wiltshire, SP3 5RG                  1
                                                                                        ..
The Bookshop$24 Magdalene Street$Cambridge                                               1
Librairie Frits Knuf$26 Rue Des Beguines, Vendôme$France                                 1
Plurabelle Books$77 Garden Walk$Cambridge$CB4 3EW                                        1
Mr J. Khalfa$D2 Great Court$Trinity College$Cambridge$CB2 1TQ                            1
Diana Parikian Rare Books$3 Caithness Road$London$W14 0JB$                               1
Name: ADDRESS1, Length: 89, dtype: int64  
![Chart](ADDRESS1.svg)
## ADDRESS2


Northampton, NN4 7YB                                                                                                                                          1
Cambridgeshire CB1 6EU                                                                                                                                        1
Swavesey, Cambridge CB4 5QG                                                                                                                                   1
Cambridge Cb3 9DR                                                                                                                                             1
Tel.: 01933 417500$Fax: 01933 417501$PRESTO! Fax: 01933 417503$TCL A/C no: 9726001-02$Finance dept. fax: 01933 417502$                                        1
TCL account= 4085000/ETRN-A$Orders contact= Amanda Hines$                                                                                                     1
Norfolk IP22 4HQ$                                                                                                                                             1
Cambridge CB5 8PX$$                                                                                                                                           1
Telephone/Fax: (01460) 54188$e-mail: inquiries@rgwatkins.co.uk                                                                                                1
Telephone: (01223) 366680                                                                                                                                     1
Cambridge CB4 2YA                                                                                                                                             1
Cambridge Cb2 3JU                                                                                                                                             1
Cambridge CB1 7ED                                                                                                                                             1
Bristol BS2 8QF$                                                                                                                                              1
EBSCO Information Sevices$(Rowecom Finance Team)$4th Floor Kingmaker House$Station Road$New Barnet EN5 1NZ                                                    1
Telephone: (01285) 810640$Fax:  (01285) 810650                                                                                                                1
Little Wymondley, Herts SG4 7JA                                                                                                                               1
Telephone: (3)38468$e-mail: jk118@cam.ac.uk$                                                                                                                  1
Tel: 0115 9708021$Fax: 0115 9787718$e-mail: 101346.3614@compuserve.com$                                                                                       1
http://www.quaritch.com                                                                                                                                       1
Telephone: (0117) 9741183$Fax: (0117) 9732901$                                                                                                                1
Vinces Road$Diss$Norfolk IP22 4HQ$                                                                                                                            1
Tel: 020 7437 5660$Priority tel: 020 7734 8766 (for account holders)  CHECK THIS (May 2011)$$$e-mail: jp@grantandcutler.com$                                  1
Tel: 01223-841988$$                                                                                                                                           1
Batheaston, Bath BA1 7DF                                                                                                                                      1
Hoddeston, EN11 0NT                                                                                                                                           1
TCL account= 4085000/ETRN$Orders contact= Amanda Hines$                                                                                                       1
Bracknell, Berkshire RG12 1FE                                                                                                                                 1
Telephone: (01434) 270046$Fax: (01434) 632931                                                                                                                 1
Telephone: (01865) 242939$Fax: (01865) 204021$e-mail: Thorntons@booknews.demon.co.uk                                                                          1
Tel: 01985-216371$Fax: 01985-212982$                                                                                                                          1
Telephone: (01223) 412002$Facsimile: 0171 700 0337                                                                                                            1
Telephone: (01239) 654404$Fax:  (01239) 654002                                                                                                                1
Tel: (01484) 644424$Fax: (01484) 645690$VAT number: 168 9221 35$Customer Services: Deborah Weavill$Area Sales Manager: David Fisher, tel.: (01728) 685480$    1
St Ives                                                                                                                                                       1
Sawston, Cambridge CB2 4EH                                                                                                                                    1
Telephone (020 8455 0031)$                                                                                                                                    1
Tel: 01223-367876                                                                                                                                             1
Nottingham NG2 4BG                                                                                                                                            1
Divine Information Services, UK Customer Services$Rue de la Prairie, Villebon sur Yvette$F-91762 Palaiseau Cedex, FRANCE                                      1
Tel: 01223 312393$Fax: 01223 315052$                                                                                                                          1
40 Newnham Road, Cambridge CB3 9EY                                                                                                                            1
Name: ADDRESS2, dtype: int64  
![Chart](ADDRESS2.svg)
## ALTCODE


Series([], Name: ALTCODE, dtype: int64)
## PHONE NUM


+44 (0)1865 792792    2
01379 647400          2
01604 732765          1
(01223) 576422        1
(020) 8319 4452       1
                     ..
020 7734 2983         1
020 7493 7160         1
00 33 254 722 656     1
(3)39493              1
01223 353468          1
Name: PHONE NUM, Length: 61, dtype: int64  
![Chart](PHONE_NUM.svg)
## EMAIL


richard.rmford@btopenworld.com                     1
mcdowell@chaucer.kc3.co.uk                         1
info@fritsknuf.com                                 1
ms@michael-silverman.com                           1
charlie@coxnbox.co.uk                              1
michael.hoskin@ntlworld.com                        1
james@libros.demon.co.uk                           1
mail@adem.co.uk                                    1
ekslibris@aol.com                                  1
ask@kenspelman.com                                 1
bib@forestbooks.co.uk                              1
grosvenorprints@btinternet.com                     1
roger@RogerGaskell.com                             1
amanda@amandahall.co.uk                            1
sales@preservationequipment.com                    1
books@jarndyce.co.uk                               1
kayhammond@hotmail.com                             1
AEustice@rowecom.co.uk                             1
See contacts at the front of Periodicals Folder    1
Cpederf@wanadoo.fr                                 1
stephen.foster@sfbooks.co.uk                       1
dsandberg@ybp.com                                  1
susanne@schulz-falster.com                         1
priley@dircon.co.uk                                1
robertshaw.books@virgin.net                        1
rarebooks@quaritch.com                             1
andrew@rarebookhunter.com                          1
johnhartbks@btopenworld.com                        1
sfalster@btinternet.com                            1
r.mengham@jesus.cam.ac.uk                          1
chr.edwards@which.net                              1
julianwhiting@aol.com                              1
Name: EMAIL, dtype: int64  
![Chart](EMAIL.svg)
## NOTE1


For rare books                                                                                        13
Rare books                                                                                             6
Mr Khalfa usually buys the books himself and brings them to the Library with an invoice                1
Dealers in antiquarian & modern prints                                                                 1
Binding                                                                                                1
Use for orders listed in their catalogues                                                              1
gp periodicals subs transferred to Swets, July 2003                                                    1
Mainly for Russian books  may include some orders for out of print titles (Nov. 1999)                  1
Hollond Law Books Scheme Account number = K39825                                                       1
Water cooler                                                                                           1
Rowecom UK/Divine Information Services periodical subs transferred to EBSCO, June 2003                 1
Dr Morris usually buys (mainly) videos/DVDs himself and brings them to the Library with an invoice     1
Mainly for rare and secondhand books                                                                   1
For rare books (and secondhand)                                                                        1
Window cleaning                                                                                        1
TCL bought a number of books from Dr Hoskins' library in March 2009 - approved by Sachiko Kusukawa     1
Periodical subscriptions transferred to Swets, July 2003                                               1
For prints and drawings                                                                                1
Fellows photos                                                                                         1
Formerly known as JMLS Library Services (TCL code = jmls) until 01.04.1997                             1
Use for orders for books listed in their catalogues                                                    1
Gives discount of 30%                                                                                  1
http://www.cpederf.com                                                                                 1
Photocopiers                                                                                           1
(Mainly) secondhand poetry and Modern Langueges, esp. poetry                                           1
Travelling rep, David Franks, rings TCL to make an appointment to bring books for selection            1
Grant & Cutler Ltd have been incorporated into Foyles as of 2011                                       1
Lists sent to TCL by Mr Khalfa                                                                         1
Rare books, autographs, manuscripts and miniatures                                                     1
For rare books and manuscripts                                                                         1
Mainly used for Law standing orders  as from Oct. 2003 used for other standing orders.                 1
Old and rare books                                                                                     1
Manuscripts (rare books fund)                                                                          1
Printing                                                                                               1
http://www.ruscico.com/                                                                                1
Send correspondence, orders, claims and payments to the UK address                                     1
Website = www.forestbooks.co.uk                                                                        1
Name changed to Library Services UK (on 01.04.1997) see information under ls                           1
Customer Service Representative for TCL: Angie Eustice Customer Service Supervisor=Debbie Marshall     1
Summer 2014 transferred about 20 journals from Swets to OUP                                            1
As from June 2004: cheques to be made out to Kay Hammond  Siddeley and Hammond A/C closed              1
Name: NOTE1, dtype: int64  
![Chart](NOTE1.svg)
## NOTE2


$0064=1697048                                                                                    2
$0064=0058955                                                                                    2
Web = http://www.rarebookhunter.com                                                              1
Pest Control                                                                                     1
Though UK customer services are based at the FRENCH ADDRESS                                      1
Gives discount of 30%                                                                            1
Contact = David Bancroft or Annie Frolet Bancroft                                                1
Rare books fund (usually)                                                                        1
$0064=1694510                                                                                    1
Mainly German studies                                                                            1
Invoice templates in a folder in the front of the Modern Languages subject A/C file              1
DVDs ordered by email                                                                            1
Mainly Hispanic studies, and Latin America                                                       1
Sold by Blackwells  became part of the Cypher Group, Autumn 1997  new address from 01.12.1997    1
Worked with vendor wb but now on his own. Makes appointment to bring books for selection         1
Existing orders handled by staff at French address (as at 01.08.2003)                            1
Formerly Siddeley & Hammond  code = sh to be retained                                            1
$0064=0047643                                                                                    1
$EDI 808.2145.0 iiiclaims@swetsblackwell.com                                                     1
Formerly Dawson Subscription Services. Acquired by RoweCom Inc. (16.09.1999)                     1
Name: NOTE2, dtype: int64  
![Chart](NOTE2.svg)
## NOTE3


$EMAILamanda.hines@blackwell.co.uk                                                      2
$EMAILinnopac@dawsonbooks.co.uk                                                         1
Relocated to Oxford (July 2001) Acquired by Divine Information Services (March 2002)    1
Invoices also on the Mac: Workroom/Asst Librarian/Invoices Khalfa & others              1
$VENDSAN=5013546040396                                                                  1
Formerly Rowecom UK  formerly Dawson Subscription Services                              1
$EMAILdsandberg@ybp.com                                                                 1
As from October 2004 Kay Hammond no longer searching for OP titles                      1
See also information in Periodicals file                                                1
$EMAILukcustserve@cup.cam.ac.uk                                                         1
UK address is to be used for payments (as at 01.08.2003)                                1
$EMAILjp@grantandcutler.com                                                             1
TCL account number = 2496                                                               1
$EMAILinnopac@dawsonbooks.co.uk.                                                        1
Name: NOTE3, dtype: int64  
![Chart](NOTE3.svg)
## SPECIAL


Series([], Name: SPECIAL, dtype: int64)
## FTP INFO


orders.gardners.com$BBFS_TRINITYCOLCAM$ZJw3mzVY    1
Name: FTP INFO, dtype: int64  
![Chart](FTP_INFO.svg)