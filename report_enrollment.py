import sys, csv, psycopg2

def print_row(term, course_code, course_name, instructor_name, total_enrollment, maximum_capacity):
	print("%6s %10s %-35s %-25s %s/%s"%(str(term), str(course_code), str(course_name), str(instructor_name), str(total_enrollment), str(maximum_capacity)) )

if len(sys.argv) != 1:
	print("Please enter only 1 argument")
	sys.exit(0)

psql_user = 'kaoaaron'
psql_db = 'kaoaaron'
psql_password = 'V00773547'
psql_server = 'localhost'
psql_port = 55555

conn = psycopg2.connect(dbname=psql_db,user=psql_user,password=psql_password,host=psql_server,port=psql_port)

cursor = conn.cursor()

try:
	insert_statement = cursor.mogrify("with\n enrolled as (select count(*) as the_count, course_code, term_code from enrollments group by course_code, term_code) select term_code, course_code, course_name, instructor, the_count, max_capacity from enrolled natural join (select term_code, course_code, course_name, instructor, max_capacity from course_offering natural join enrollments) as T")
	cursor.execute(insert_statement)
			
	rows_found = 0
	while True:
		row = cursor.fetchone()
		if row is None:
			break
		rows_found += 1
		print_row(row[0], row[1], row[2], row[3], row[4], row[5])
	

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