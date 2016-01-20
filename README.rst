SRMLF
=====

.. image:: https://travis-ci.org/gordon-/srmlf.svg?branch=master
    :target: https://travis-ci.org/gordon-/srmlf
.. image:: https://coveralls.io/repos/github/gordon-/srmlf/badge.svg?branch=master :target: https://coveralls.io/github/gordon-/srmlf?branch=master

Short Reckonings Make Long Friends — a lightweight reckoning tracker written in
Python

Dependencies
============

TODO

Install
=======

    python setup.py install

Usage
=====

1. Create a project

    srmlf init <project_name> Alice Bob

This will create a project named `<project_name>`, with Alice and Bob as
participants. This project has no fixed total amount, but you can specify one
with:

    srmlf init <project_name> -t 1000 Alice Bob

This fixes the total amount for project `<project_name>` to 1000 (currency does
not matter here).

If you want to include spaces in user names, just add quotes around the name.

2. Add funds to a project

    srmlf add <project_name> 'Test contribution' Alice 100

This simply adds 100 to Alice’s contribution to `<project_name>`, marked to
current date, by default. If you want to add a past contribution, specify the
date with:

    srmlf add <project_name> -d 2016-01-19 Alice 100

Date is given in international format.

If you want to add a multi-user contribution, add as many user:value couples as
necessary:

    srmlf add <project_name> Alice:100 Bob:50

If you want to add a new member for the project, just add its name in a
contribution. But if you misspell a user’s name, for example by writing it
lowercase, SRMLF will find it instead of creating another user.

3. Edit contributions

This is not managed by SRMLF yet. But guess what, the source file is a simple
CSV, so all you have to do is to edit the `data/<project_name>.csv` file.

4. Sum up

    srmlf view <project_name>

This shows the status of the project, in a format looking like this:

    +-------------------+------------+--------+--------+
    |   <project_name>  |    Date    |  Alice |   Bob  |
    +-------------------+------------+--------+--------+
    | Test contribution | 2016-01-19 |   100  |   50   |
    +-------------------+------------+--------+--------+
    |       Total       |            |   100  |   50   |
    +-------------------+------------+--------+--------+
    |                   |            | 66.66% | 33.33% |
    +-------------------+------------+--------+--------+
    |                   |            |       150       |
    +-------------------+------------+--------+--------+

If you specified a total amount for the project, the percentage takes it into
account.
