import psycopg2, sys

psql_user = 'kaoaaron'
psql_db = 'kaoaaron'
psql_password = 'V00773547'
psql_server = 'localhost'
psql_port = 55555

conn = psycopg2.connect(dbname=psql_db,user=psql_user,password=psql_password,host=psql_server,port=psql_port)

cursor = conn.cursor()

def print_header(student_id, student_name):
	print("Transcript for %s (%s)"%(str(student_id), str(student_name)) )
	
def print_row(course_term, course_code, course_name, grade):
	if grade is not None:
		print("%6s %10s %-35s   GRADE: %s"%(str(course_term), str(course_code), str(course_name), str(grade)) )
	else:
		print("%6s %10s %-35s   (NO GRADE ASSIGNED)"%(str(course_term), str(course_code), str(course_name)) )


if len(sys.argv) < 2:
	print('Usage: %s <student id>'%sys.argv[0], file=sys.stderr)
	sys.exit(0)
	
student_id = sys.argv[1]

try:
	insert_statement = cursor.mogrify("select student_name, term_code, course_code, course_name, grade from enrollments natural join course_offering where student_id = '" + student_id + "' order by term_code, course_code")
	cursor.execute(insert_statement)
			
	flag = 0
	
	rows_found = 0
	while True:
		row = cursor.fetchone()
		if flag == 0:
			flag = 1
			print_header(student_id, row[0])
		
		if row is None:
			break
		rows_found += 1
		print_row(row[1], row[2], row[3], row[4])

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
except TypeError:
	print("Invalid Parameters or No Results")
	sys.exit()
	
cursor.close()
conn.close()