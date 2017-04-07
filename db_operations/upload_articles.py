import numpy
import psycopg2
import pandas as pd

articles = pd.read_csv('../scrapers/azbuka_scraper/data/azbuka_raw.csv', sep='\t', encoding='utf-8').values

conn = psycopg2.connect("host=host port=0000 dbname=dbname user=user password=password")
cur = conn.cursor()

cur.execute("DELETE FROM Articles;")

for idx, row in zip(range(articles.shape[0]), articles):
    if idx % 100 == 0:
        print "{0}/{1}".format(idx, articles.shape[0])
    if row[2] is numpy.nan:
        cur.execute("INSERT INTO Articles (id, name, url) VALUES (%s, %s, %s);",
                    (idx, row[0], row[1]))
    else:
        cur.execute("INSERT INTO Articles (id, name, url, preview, path) VALUES (%s, %s, %s, %s, %s);",
                    (idx, row[0], row[1], row[2], row[3]))

# cur.execute("Select * FROM Articles")
# colnames = [desc[0] for desc in cur.description]
# print colnames
# print cur.fetchone()

conn.commit()
cur.close()
conn.close()