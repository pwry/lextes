from __future__ import division
from db import init_db

# Every link is either checked (HTTP(S)) or unchecked (FTP).
def num_links(sql):
	return sql.execute("SELECT COUNT(DISTINCT url) FROM links").fetchone()[0]

def num_checked_links(sql):
	return sql.execute("SELECT COUNT(DISTINCT checks.link) FROM checks").fetchone()[0]

def num_unchecked_links(sql):
	return sql.execute("SELECT COUNT(DISTINCT l.id) FROM links AS l WHERE NOT EXISTS(SELECT link FROM checks WHERE l.id = checks.link)").fetchone()[0]

# Every checked link is either consistent (returns same HTTP status every check) or inconsistent.
def num_con_links(sql):
        return sql.execute("SELECT COUNT(DISTINCT checks.link) FROM checks WHERE checks.link NOT IN (\
                                SELECT DISTINCT c1.link FROM checks AS c1 JOIN checks AS c2 ON c1.link = c2.link WHERE c1.code < c2.code)").fetchone()[0]

def con_links(sql, code):
	return sql.execute("SELECT DISTINCT checks.link, links.url FROM checks JOIN links ON checks.link = links.id WHERE checks.link NOT IN (\
				SELECT DISTINCT c1.link FROM checks AS c1 JOIN checks AS c2 ON c1.link = c2.link WHERE c1.code < c2.code)\
				AND checks.code = ?", (code,)).fetchall()

def con_nw_links(sql): # Don't rely on this for counts: the same link may return a different message even if the code is the same.
	# Might want to fix this eventually: pull distinct link IDs from checks in subquery and get URL/code/message from joins onto that?
	return sql.execute("SELECT DISTINCT checks.link, links.url, checks.code, checks.message FROM checks JOIN links ON checks.link = links.id \
				WHERE checks.link NOT IN\
				(SELECT DISTINCT c1.link FROM checks AS c1 JOIN checks AS c2 ON c1.link = c2.link WHERE c1.code <> c2.code)\
				AND checks.code <> 200").fetchall()

def num_con_nw_links(sql):
	return sql.execute("SELECT COUNT(DISTINCT c.link) FROM checks AS c WHERE c.link NOT IN\
				(SELECT DISTINCT c1.link FROM checks AS c1 JOIN checks AS c2 ON c1.link = c2.link WHERE c1.code <> c2.code)\
				AND c.code <> 200").fetchone()[0]

def incon_links(sql): # Don't rely on this for counts either; if one link returns 3+ distinct codes, those will show up as 2+ rows
	return sql.execute("SELECT DISTINCT c1.link, links.url, c1.code, c2.code FROM checks AS c1 JOIN links ON c1.link = links.id \
				JOIN checks AS c2 ON c1.link = c2.link WHERE c1.code < c2.code ORDER BY c1.link").fetchall()

def num_incon_links(sql):
	return sql.execute("SELECT COUNT(DISTINCT c1.link) FROM checks AS c1 JOIN checks AS c2 ON c1.link = c2.link WHERE c1.code < c2.code").fetchone()[0]

# Every inconsistent link either works sometimes or doesn't.
def num_incon_w(sql):
	return sql.execute("SELECT COUNT(DISTINCT c1.link) FROM checks AS c1 JOIN checks AS c2 ON c1.link = c2.link WHERE c1.code <> c2.code AND c1.code = 200").fetchone()[0]

def num_incon_nw(sql): # unreasonably slow
	return sql.execute("SELECT COUNT(DISTINCT incon.link) FROM (SELECT c3.link, c3.code FROM checks AS c3 JOIN checks AS c4 ON c3.link = c4.link\
		WHERE c3.code <> c4.code) incon\
		WHERE NOT EXISTS(SELECT c1.link FROM checks AS c1 WHERE c1.code = 200 AND c1.link = incon.link)").fetchone()[0]

# percentize
def c(a, b):
	return round(a / b * 100, 2)

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser("Process data from links.sqlite.")
	parser.add_argument("-d", dest="detailed", action="store_const", const=True, default=False, help="Display detailed output.")
	parser.add_argument("-s", dest="sanity_check", action="store_const", const=True, default=False, help="Display sanity checks.")
	args = parser.parse_args()
	conn, sql = init_db()
	total_links = num_links(sql)
	print "There are {0} links in the database.".format(total_links)
	num_checked = num_checked_links(sql)
	num_unchecked = num_unchecked_links(sql)
	print "{0} links were checked. {1} links weren't -- these are probably FTP.".format(num_checked, num_unchecked)
	num_con = num_con_links(sql)
	num_con_w = len(con_links(sql, 200))
	num_con_nw = num_con_nw_links(sql)
	print "Of the checked links, {0} ({1}%) were consistent: they returned the same HTTP status at every check. {2} ({3}%) of these worked (returned 200 OK)."\
		.format(num_con, c(num_con, num_checked), num_con_w, c(num_con_w, num_checked))
	num_incon = num_incon_links(sql)
	num_incon_w = num_incon_w(sql)
	num_incon_nw = num_incon_nw(sql)
	print "There were {0} inconsistent links. Of these, {1} ({2}%) worked sometimes, and {3} ({4}%) never worked, but for different reasons across checks."\
		.format(num_incon, num_incon_w, c(num_incon_w, num_checked), num_incon_nw, c(num_incon_nw, num_checked))
	if args.sanity_check:
		num_working = sql.execute("SELECT COUNT(DISTINCT link) FROM checks WHERE code = 200").fetchone()[0]
		num_not_working = sql.execute("SELECT COUNT(DISTINCT link) FROM checks WHERE code <> 200").fetchone()[0]
		print
		print "{0} {1} Links should either be checked or unchecked.".format(total_links, num_checked + num_unchecked)
		print "{0} {1} Checked links should either be consistent or be inconsistent.".format(num_checked, num_con + num_incon)
		print "{0} {1} Consistent links should either always work or never work.".format(num_con, num_con_w + num_con_nw)
		print "{0} {1} Inconsistent links should either work sometimes or never work.".format(num_incon, num_incon_w + num_incon_nw)
		print "{0} {1} Links that returned a 200 OK should be either consistent or inconsistent.".format(num_working, num_con_w + num_incon_w)
		print "{0} {1} Links that returned something other than a 200 OK should be either consistently not working or inconsistent.".format(num_not_working, \
			num_con_nw + num_incon_w + num_incon_nw)
