NOTES
======

If you haven't used this for a while or this is your first time, follow these steps.

- Let's make sure that you can edit files!
  * At the moment, I am trying out ReText as the rst editor

  * I created a directory with ReText install in a ``pipenv`` environment. So 

  ..  code-block:: sh

      cd ReText
      pipenv shell
      python -m ReText

  * A window should open and then you can edit your file with a preview.

- Now what? If you are writing a commentary on a sutta, then you probably would like to use `palitype <readme/palitype>`_.
- After palitype produced the ``rst`` file, you can see the end resulting html by using `pelican <readme/pelican


.. _readme/palitype:

:index:`Palitype`
------------------
Palitype is a preprocessor on markup. It takes text with quotes in different
languages. It then:

1.  Reads a strict_yaml file https://github.com/crdoconnor/strictyaml.
    The yaml file indicates the delimiters that indicate the target text
    and the mark-up that will envelope the target text.
    
    Example:
        Text is presented that contains English, Pali and Sanskrit.
        
            DELIMITER1 English DELIMITER2 Pali DELIMITER3 Sanskrit DELIMITER4

2.  The first line in the text file refers to the yml file that contains the delimiters
    .. include:: palitype_instructions.yml


Use
^^^

..  code-block:: sh
        
    cd palitype
    pipenv shell
    (palitype)% cd ../content/pages
    (palitype)% python ../../palitype/cli.py SN001.txt


:index:`Tests`
^^^^^^^^^^^^^^^^^^^^^
The ``palitype`` tests are run:

.. code-block:: sh

    cd palitype
    pipenv run python -m pytest

Some options:

.. code-block:: sh

     pipenv run python -m pytest -x           # stop after first failure
     pipenv run python -m pytest --maxfail=2  # stop after two failures


coverage.py
^^^^^^^^^^^^
To guage effectiveness of tests, use ``coverage.py``.


:index:`Pelican`
-------
After preprocessing the text file with palitype, run pelican to generate the html files.

..  code-block:: sh
    
    cd ~/My\ Buddhism/SN
    pelican content
    pelican --listen

TO change a theme, see `Pelican themes`_ .

.. _Pelican themes: https://github.com/getpelican/pelican-themes/blob/master/README.rst

but here, the ``m.css`` is used.

The ``pelicanconf.py`` file is

.. literalinclude:: ../../../../../pelicanconf.py
   :language: python

This is placed in the main directory where ``pelican`` is executed. All the content is in the ``content`` folder beneath it.

The default theme is ``m-theme-dark.css`` but this them will indent all paragraphs by 1.5rem. To avoid this, change this line::

  --paragraph-indent:

to::

  --paragraph-indent: 0rem; 



On web browser, go to ``http://localhost:8000``


Environment
-----------

Let's use pipenv as the package manager.
..  code-block:: sh

    conda activate SN

Sphinx
------  
..  code-block:: sh

    cd py4web/apps/samyutta/palitype/docs
    sphinx-quickstart

Added:
    
..  code-block:: python

    sys.path.insert(0, os.path.abspath('..'))
    sys.path.append(os.path.abspath('.'))

to the ``conf.py``. The second line is to read the ``ipython`` directives from
a directory within ``docs``. iPython directive was placed in there so that the
extensions list in ``conf.py`` looks like:

..  code-block:: python

    extensions = ['sphinx.ext.autodoc', 
                  'sphinx.ext.coverage',
                  'sphinx.ext.napoleon',
                  'sphinxext.ipython_console_highlighting',
                  'sphinxext.ipython_directive'
    ]

The ``sphinxext`` directory was obtained from https://github.com/ipython/ipython/tree/master/IPython

Generate html from this ``README.rst`` file by adding the line::

    .. include:: ../README.rst

in the ``docs/read.rst``.


..  code-block:: sh

    cd docs
    make html

Gotchas
^^^^^^^
Don't use any spaces in paths. Spaces in pathnames will generate bookmark errors.

Spyder
------
Project uses ``Spyder`` as general IDE and editor.

..  code-block:: sh

    cd SN
    spyder &

docformatter
------------

..  code-block:: sh

    conda install -c conda-forge docformatter
    docformatter --in-place example.py
    docformatter --recursive --in-place dir

yapf
----
``yapf`` is a python formatter.

..  code-block:: sh

    conda install -c conda-forge yapf
    yapf --recursive --in-place dir

If these settings in ``setup.cfg``, google styling is used and this has the 
least errors after running ``pylama``.::

    [yapf]
    based_on_style = google
    spaces_before_comment = 4
    split_before_logical_operator = true

Pylint
------


Git
---
https://realpython.com/python-git-github-intro/
(use gitignore.io to generate ``.gitignore`` file using 'Python', 'mac' and 'git' as seeds)

..  code-block:: sh

    Buddhism % cd SN/py4web/apps/samyutta/palitype
    palitype % git config --global user.name "your name goes here"
    palitype % git init
    Initialized empty Git repository in ...

Add ``docs/sphinxext/`` to ``.gitignore`` To remove staged files use:

..  code-block:: sh

    palitype % git reset docs/sphinxext/

To commit all

..  code-block:: sh

    palitype % git commit -am 'Initial commit'

Wily
----
Project uses ``wily`` as mentioned at https://realpython.com/python-refactoring/


``wily`` analyses the code and calculates a mertic that describes the complexity
of the code.


coverage.py
^^^^^^^^^^^
To guage effectiveness of tests, use ``coverage.py``.
    
Database
--------
Database set up uses a postgres docker, so an postgresql image is first
downloaded https://hub.docker.com
Then:

..  code-block:: sh
    
    docker run --name postgres -p 5433:5432 -v /Users/ben/Databases/sn:/var/lib/postgresql/data -e POSTGRES_PASSWORD=time67docker

Note that:

1.  The port has changed for the host. The host port is 5433
2.  The location of the database is in a host directory.
    So in ``settings.py``:
    
    .. code-block:: python
        
        # DB_FOLDER:    Sets the place where migration files will be created
        #               and is the store location for SQLite databases
        DB_FOLDER = "/Users/ben/Databases/sn/py4web"
        DB_URI = "postgres://postgres:time67docker@localhost:5433/postgres"

Now in ``common.py``, ``db`` is declared with the ``check_reserved = ["postgres"]``:

..  code-block:: python
    
    db = DAL(
        settings.DB_URI,
        folder=settings.DB_FOLDER,
        pool_size=settings.DB_POOL_SIZE,
        migrate=settings.DB_MIGRATE,
        fake_migrate=settings.DB_FAKE_MIGRATE,
        check_reserved=['postgres'],
    )


Postgresql Notes
----------------
Use https://www.postgresql.org/docs/current/pgtrgm.html
