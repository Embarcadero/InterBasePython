# InterBase Driver for Python, supporting 32-bit and 64-bit

[InterBase Documentation](https://docwiki.embarcadero.com/InterBase/2020/en/Main_Page) \* 
[InterBase Source](https://github.com/Embarcadero/InterBasePython) \* 
[Based On FDB](http://www.firebirdsql.org/en/devel-python-driver/)

Changes implemented are based on this blog post

InterBase Driver for Python is a [Python](http://python.org) library package that implements
[Python Database API 2.0](http://www.python.org/dev/peps/pep-0249/)-compliant support for the Embarcadero SQL Database
[InterBase](https://interbase.com/) ®. In addition to the minimal
feature set of the standard Python DB API, InterBase Driver for Python also exposes the entire
native (old-style) client API of the database engine. Notably:

  - Automatic data conversion from strings on input.
  - Automatic input/output conversions of textual data between UNICODE
    and database character sets.
  - Support for prepared SQL statements.
  - Multiple independent transactions per single connection.
    access specifications.
  - Distributed transactions.

Install (32-bit or 64-bit version of python 3.* required)

You can use one of the following ways to do it.

`pip install interbase`

`pip install git+https://github.com/Embarcadero/InterBasePython.git`

`pip install git+ssh://git@github.com/Embarcadero/InterBasePython.git`

To create a test DB:

`cd test/files && isql -i create-test-db.sql`
