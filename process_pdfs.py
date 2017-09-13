from db import init_db
import sys, codecs, pyPdf

def find_pdf_links(filename):
	pdf_file = open(filename)
	pdf = pyPdf.PdfFileReader(pdf_file)
	pdf_links = []
	pdf_pages = pdf.getNumPages()
	for i in range(pdf_pages):
		page = pdf.getPage(i).getObject()
		if page.has_key('/Annots'):
			for k in page['/Annots']:
				annot = k.getObject()
				if annot.has_key('/A') and annot['/A'].has_key('/URI'):
					pdf_links.append(annot['/A']['/URI'])
	return pdf_links

def filter_links(links):
	to_filter = ['www.aanda.org', 'www.edpsciences.org', 'dexter.edpsciences.org', 'dx.doi.org']
	return [l for l in links if not any([l.find(u) > -1 for u in to_filter])]

def process_papers(filenames):
	conn, sql = init_db()
	processed_files = 0
	added_links = 0
	errored_files = []
	for filename in filenames:
		print("Reading file {0}".format(filename))
		try: 
			links = filter_links(find_pdf_links(filename))
		except pyPdf.utils.PdfReadError:
			print("Couldn't read file")
			errored_files.append(filename)
			continue
		for link in links:
			print("\tAdding link {0}".format(link))
		links_and_filenames = zip(links, [filename] * len(links))
		sql.executemany("INSERT INTO links(url, filename) VALUES(?, ?)", links_and_filenames)
		processed_files += 1
		added_links += len(links)
	conn.commit()
	conn.close()
	print("--- Complete! ---")
	print("Processed {0} files, added {1} links".format(processed_files, added_links))
	if len(errored_files) == 0:
		print("No file read errors!")
	elif len(errored_files) == 1:
		print("1 file read error:\n\t{0}".format(errored_files[0]))
	else:
		print("{0} file read errors:".format(len(errored_files)))
		for f in errored_files:
			print("\t" + f)

if __name__ == "__main__":
	process_papers(sys.argv[1:])
