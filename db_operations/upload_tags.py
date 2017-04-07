import psycopg2
import cPickle

conn = psycopg2.connect("host=host port=0000 dbname=dbname user=user password=password")
cur = conn.cursor()

tags_raw = cPickle.load(open('tags_raw.p', 'rb'))
for idx, tag in zip(range(tags_raw.shape[0]), tags_raw):
    if idx % 100 == 0:
        print idx
    cur.execute("INSERT INTO Tags (id, name) VALUES (%s, %s);", (idx, tag))

cur.execute("Select * FROM Tags")
colnames = [desc[0] for desc in cur.description]
print colnames
print cur.fetchone()[1]

conn.commit()
cur.close()
conn.close()
