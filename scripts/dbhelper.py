import psycopg2
import psycopg2.extras

def db_config():
	
	return { "host" : "localhost", "database": "pkt", "username": "postgres","password": "password" }

def GetData(strquery,firstRowOnly):
	conn = None
	try:

		retval = None
		dbconf = db_config()
		# conn = psycopg2.connect(host=db_host,database=db_name, user=db_user, password=dp_pass)
		conn = psycopg2.connect(host=dbconf["host"],database=dbconf["database"], user=dbconf["username"], password=dbconf["password"])
		cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
		cur.execute(strquery)
		
		if cur.rowcount > 0:
			if firstRowOnly: 
				retval = cur.fetchone()
			else:
				retval = cur.fetchall()

		cur.close()

	except (Exception, psycopg2.DatabaseError) as error:
		print(error)

	finally:
		if conn is not None:
			conn.close()

		return retval

def ExecuteQuery(strquery,params,singleRowOnly,fetchResult):
	try:

		retval = 0;
		dbconf = db_config()
		# conn = psycopg2.connect(host=db_host,database=db_name, user=db_user, password=dp_pass)
		conn = psycopg2.connect(host=dbconf["host"],database=dbconf["database"], user=dbconf["username"], password=dbconf["password"])
		cur = conn.cursor()
		if singleRowOnly:
			cur.execute(strquery,params)
			if fetchResult: retval = cur.fetchone()[0]
		else:
			cur.executemany(strquery,params)	
			if fetchResult: retval = 1	
		
		conn.commit()
		cur.close()

	except (Exception, psycopg2.DatabaseError) as error:
	    print(error)

	finally:
		if conn is not None:
			conn.close()
		
		if fetchResult: return retval
