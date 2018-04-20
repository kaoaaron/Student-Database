import sys, csv, psycopg2

if len(sys.argv) < 3:
	print('Usage: %s <course code> <term>'%sys.argv[0], file=sys.stderr)
	sys.exit(0)

psql_user = 'kaoaaron'
psql_db = 'kaoaaron'
psql_password = 'V00773547'
psql_server = 'localhost'
psql_port = 55555

conn = psycopg2.connect(dbname=psql_db,user=psql_user,password=psql_password,host=psql_server,port=psql_port)

cursor = conn.cursor()

def print_header(course_code, course_name, term, instructor_name):
	print("Class list for %s (%s)"%(str(course_code), str(course_name)) )
	print("  Term %s"%(str(term), ) )
	print("  Instructor: %s"%(str(instructor_name), ) )
	
def print_row(student_id, student_name, grade):
	if grade is not None:
		print("%10s %-25s   GRADE: %s"%(str(student_id), str(student_name), str(grade)) )
	else:
		print("%10s %-25s"%(str(student_id), str(student_name),) )

def print_footer(total_enrolled, max_capacity):
	print("%s/%s students enrolled"%(str(total_enrolled),str(max_capacity)) )


course_code, term = sys.argv[1:3]

try:
	insert_statement = cursor.mogrify("with\n enrolled as (select count(*) as the_count, course_code, term_code from enrollments group by course_code, term_code) select course_code, course_name, term_code, instructor, the_count, max_capacity from enrolled natural join (select distinct term_code, course_code, course_name, instructor, max_capacity from course_offering natural join enrollments where term_code = '" + term + "' and course_code = '" + course_code + "') as T;")
	cursor.execute(insert_statement)
			
	row = cursor.fetchone()

	print_header(row[0], row[1], row[2], row[3])
	
	enrolled_count = row[4]
	max_cap = row[5]

	insert_statement = cursor.mogrify("select student_id, student_name, grade from enrollments where course_code = '" + course_code + "'and term_code = '" + term + "';")
		
	cursor.execute(insert_statement)
	
	rows_found = 0
	while True:
		row = cursor.fetchone()
		if row is None:
			break
		rows_found += 1
		print_row(row[0], row[1], row[2])
		
	print_footer(enrolled_count, max_cap)

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