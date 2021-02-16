.. meta::
   :description: Mergify Documentation for Rebase Action
   :keywords: mergify, rebase, pull request
   :summary: Rebase a pull request on top of its base branch.
   :doc:icon: undo

.. _rebase action:

rebase
======

The ``rebase`` action will rebase the pull request against its base branch.

.. list-table::
  :header-rows: 1
  :widths: 1 1 1 2

  * - Key Name
    - Value Type
    - Default
    - Value Description

  * - ``bot_account``
    - :ref:`data type template`
    -
    - For certain actions, such as rebasing branches, Mergify has to
      impersonate a GitHub user. You can specify the account to use with this
      option. If no ``bot_account`` is set, Mergify picks randomly one of the
      organization users instead. The user account **must** have already been
      logged in Mergify dashboard once.

.. warning::

   Be aware that rebasing force-pushes the pull request head branch: any change
   done to that branch while Mergify is rebasing will be lost.

.. warning::

   If the repository is bigger than 512 MB, the ``rebase`` action is only
   available for `Essential and Premium  Plan subscribers <https://mergify.io/pricing>`_.
   |essential plan tag|
   |premium plan tag|

.. include:: ../global-substitutions.rst