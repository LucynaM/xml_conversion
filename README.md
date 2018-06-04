JPK_VAT file conversion (xml => db => excel)

1. xml file structure translation into Django db models (according to documentation posted on
 https://www.mf.gov.pl/krajowa-administracja-skarbowa/dzialalnosc/struktury-jpk)
2. saving data from xml file as database records
3. writing db records as excel file with XlsxWriter (in progress)
4. Files uplaod, files download
5. user registration panel, login/logout mechanism
7. deleting xml file after processing
8. ToDo:
    * looking for a more efficient way of processing big xml files (iterparse, lxml, sax???) in order to handle JPK_KR
    * layout deployment (frontend)
