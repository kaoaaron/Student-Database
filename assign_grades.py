import sys, csv, psycopg2

if len(sys.argv) < 2:
	print("Usage: %s <input file>",file=sys.stderr)
	sys.exit(0)
	
input_filename = sys.argv[1]

psql_user = 'kaoaaron'
psql_db = 'kaoaaron'
psql_password = 'V00773547'
psql_server = 'localhost'
psql_port = 55555

conn = psycopg2.connect(dbname=psql_db,user=psql_user,password=psql_password,host=psql_server,port=psql_port)

cursor = conn.cursor()

# Open your DB connection here

with open(input_filename) as f:
	for row in csv.reader(f):
		if len(row) == 0:
			continue #Ignore blank rows
		if len(row) != 4:
			print("Error: Invalid input line \"%s\""%(','.join(row)), file=sys.stderr)
			break
		course_code,term,student_id,grade = row
		
		try:
		
			insert_statement = cursor.mogrify("update enrollments set grade = %s where (student_id = %s and term_code = %s and course_code = %s);", (row[3], row[2], row[1], row[0]))
			
			cursor.execute(insert_statement)
			
		except psycopg2.ProgrammingError as err: 
			#ProgrammingError is thrown when the database error is related to the format of the query (e.g. syntax error)
			print("ProgrammingError:",file=sys.stderr)
			print(err,file=sys.stderr)
			sys.exit()
			
		except psycopg2.IntegrityError as err: 
			#IntegrityError occurs when a constraint (primary key, foreign key, check constraint or trigger constraint) is violated.
			print("IntegrityError:",file=sys.stderr)
			print(err,file=sys.stderr)
			sys.exit()
		
		except psycopg2.InternalError as err:  
			#InternalError generally represents a legitimate connection error, but may occur in conjunction with user defined functions.
			#In particular, InternalError occurs if you attempt to continue using a cursor object after the transaction has been aborted.
			#(To reset the connection, run conn.rollback() and conn.reset(), then make a new cursor)
			print("IntegrityError:",file=sys.stderr)
			print(err,file=sys.stderr)
			sys.exit()

conn.commit()
cursor.close()
conn.close()
		