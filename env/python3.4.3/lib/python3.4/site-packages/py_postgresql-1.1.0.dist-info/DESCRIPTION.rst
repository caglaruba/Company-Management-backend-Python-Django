
py-postgresql is a set of Python modules providing interfaces to various parts
of PostgreSQL. Notably, it provides a pure-Python driver + C optimizations for
querying a PostgreSQL database.

http://python.projects.postgresql.org

Features:

 * Prepared Statement driven interfaces.
 * Cluster tools for creating and controlling a cluster.
 * Support for most PostgreSQL types: composites, arrays, numeric, lots more.
 * COPY support.

Sample PG-API Code::

	>>> import postgresql
	>>> db = postgresql.open('pq://user:password@host:port/database')
	>>> db.execute("CREATE TABLE emp (emp_first_name text, emp_last_name text, emp_salary numeric)")
	>>> make_emp = db.prepare("INSERT INTO emp VALUES ($1, $2, $3)")
	>>> make_emp("John", "Doe", "75,322")
	>>> with db.xact():
	...  make_emp("Jane", "Doe", "75,322")
	...  make_emp("Edward", "Johnson", "82,744")
	...

There is a DB-API 2.0 module as well::

	postgresql.driver.dbapi20

However, PG-API is recommended as it provides greater utility.

Once installed, try out the ``pg_python`` console script::

	$ python3 -m postgresql.bin.pg_python -h localhost -p port -U theuser -d database_name

If a successful connection is made to the remote host, it will provide a Python
console with the database connection bound to the `db` name.


History
-------

py-postgresql is not yet another PostgreSQL driver, it's been in development for
years. py-postgresql is the Python 3 port of the ``pg_proboscis`` driver and
integration of the other ``pg/python`` projects.


