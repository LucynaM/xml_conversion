JPK_VAT & JPK_KR file conversion (xml => excel)

1. Map the structure of tags from xml files by spliting them into file-tables-tags scheme according to instruction accessible in https://www.mf.gov.pl/krajowa-administracja-skarbowa/dzialalnosc/struktury-jpk
2. Unable the edition of tag structure in order to adjust them to changes released by Ministry of Finance (add new tables and tags, edit existing tables, tags, delete existng tables, tags)
3. Unable the creation of new structure of tags for new types of files
4. Process loaded file:
* Create interface that allows user to load a file
* Recognise the type of file based on its namespace tag
* Process data stored in loaded file in order to save them as an array of dictionaries with lxml
* Save data obtained in that way as a xmlx file with XlsxWriter
* Delete xml file after processing it
5. ToDo:
* Layout deployment
* Handle zip files