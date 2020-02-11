import psycopg2

conn = psycopg2.connect(database="test", user="baikai", password="baikai#1234", host="localhost", port="5432")

print("Opened database successfully.")

cur = conn.cursor()
cur.execute("insert into ddns_info (request_time, ip, domain, sub_domain) "
            "values (now(), '127.0.0.1', 'baikai.top', 'a')")

conn.commit()