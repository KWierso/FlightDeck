Installation on the server
==========================

FligtDeck depends on Python, virtualenv, virtualenvwrapper, mysql, git, 
mercurial, xulrunner.

* Download the code::

    git clone git://github.com/mozilla/FlightDeck.git -b production
    # or -b staging if staging server

.. include:: ../_includes/installation_create_dirs.rst

.. include:: ../_includes/installation_local_config.rst

.. include:: ../_includes/installation_virtual_env.rst

.. include:: ../_includes/installation_sdk.rst

.. include:: ../_includes/installation_database.rst

* Deactivate the virtual environment::

   deactivate

* Configure Apache, a sample config is in ``apache/config_local-default.wsgi``. Please copy to ``apache/config_local.wsgi`` before modifying.

