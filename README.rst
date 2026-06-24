Open edX Events 2 n8n
########################

|ci-badge| |license-badge|

A ready-to-use repository demonstrating how to use Open edX Events for building workflows and automating integrations. It serves as a starting point for more advanced use cases. Explore `Real-Life Use Cases for Open edX Events`_ to see more complex implementations from the Open edX Community

Purpose
********

This repository demonstrates how to connect Open edX registration, enrollment, and grade change events to external tools via n8n, enabling easier automation workflows through this third-party service.

Open edX Events are a powerful feature that allows developers to listen to key events in the Open edX platform and trigger custom actions based on them. This can be useful for a variety of use cases, such as:

- Sending welcome emails to new users
- Logging new enrollments to external CRMs
- Triggering events like email follow-ups for grade updates

By sending key event data to n8n, Open edX users can leverage the integration ecosystem of n8n without additional development effort.

Getting Started with Development
********************************

Please see the Open edX documentation for `guidance on Python development`_ in this repo.

.. _guidance on Python development: https://docs.openedx.org/en/latest/developers/how-tos/get-ready-for-python-dev.html

Deploying
*********

See the Usage section below for instructions on how to deploy this plugin. Also, see the `Tutor documentation`_ for more information on deploying extra requirements.

Getting Help
************

Documentation
=============

Refer to the `Open edX Events documentation`_ to learn about implementing and working with events. This documentation details how to use the repository to integrate with third-party services, such as n8n Webhooks, through events.

You can review the rendered documentation at https://abstract-tech.github.io/openedx-events-2-n8n/.

Features
--------

- **Event Handlers**: Listen to Open edX Events using Django signals and send data to n8n.
- **Webhook Integration**: Send event data to n8n webhooks for further processing.
- **Customizable**: Easily extend the repository to handle additional events or integrate with other services.
- **Ready-to-Use**: Install the package and configure webhooks to start sending events to n8n.

Supported Events
----------------

+-------------------------------------+-----------------------------------------------------------------+---------------------------------------------------------------------+
| **Event Name**                      | **Event Type**                                                  | **Description**                                                     |
+=====================================+=================================================================+=====================================================================+
| `STUDENT_REGISTRATION_COMPLETED`_   | org.openedx.learning.student.registration.completed.v1          | Triggered when a user completes registration in the LMS.            |
+-------------------------------------+-----------------------------------------------------------------+---------------------------------------------------------------------+
| `COURSE_ENROLLMENT_CREATED`_        | org.openedx.learning.course.enrollment.created.v1               | Triggered upon successful course enrollment.                        |
+-------------------------------------+-----------------------------------------------------------------+---------------------------------------------------------------------+
| `PERSISTENT_GRADE_SUMMARY_CHANGED`_ | org.openedx.learning.course.persistent_grade_summary.changed.v1 | Triggered when a persistent grade summary is updated. This happens  |
|                                     |                                                                 | when a grade changes in a course.                                   |
+-------------------------------------+-----------------------------------------------------------------+---------------------------------------------------------------------+

How Does it Work?
-----------------

Each of the above events is handled by Django Signal handlers. When these signals are emitted, they are intercepted by handlers defined in the repository, which transform and forward the event data to a `n8n webhook`_.

Django Signal Handlers
~~~~~~~~~~~~~~~~~~~~~~

In the file `handlers.py`_, handlers listen to Django signals using the standard `receiver`_ decorator:

.. code-block:: python

    from django.dispatch import receiver
    from openedx_events.signals import STUDENT_REGISTRATION_COMPLETED

    @receiver(STUDENT_REGISTRATION_COMPLETED)
    def send_user_data_to_webhook(signal, sender, user, metadata, **kwargs):
        n8n_payload = {
            "user": asdict(user),
            "event_metadata": asdict(metadata),
        }
        requests.post(
            settings.N8N_REGISTRATION_WEBHOOK,
            json=flatten_dict(n8n_payload),
            timeout=N8N_REQUEST_TIMEOUT,
        )

- The ``receiver`` decorator listens to the ``STUDENT_REGISTRATION_COMPLETED`` signal.
- The handler function ``send_user_data_to_webhook`` extracts the user and metadata from the signal.
- The ``N8N_REGISTRATION_WEBHOOK`` URL is configured as a Django settings by using a `Tutor plugin`_.
- The extracted data is formatted into a payload and sent to the n8n webhook for further processing.

App Configuration (``apps.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Django app is configured using an ``AppConfig`` to automatically register handlers on startup.

.. code-block:: python

    class OpenedxEvents2N8nConfig(AppConfig):
        name = "openedx_events_2_n8n"

        def ready(self):
            from openedx_events_2_n8n import handlers

Usage
-----

To use this plugin, follow these steps:

1. Install the plugin in your Open edX image using Tutor's ``OPENEDX_EXTRA_PIP_REQUIREMENTS`` configuration setting:

.. code-block:: yaml

    OPENEDX_EXTRA_PIP_REQUIREMENTS:
    - git+https://github.com/Abstract-Tech/openedx-events-2-n8n.git@X.Y.Z

2. Launch the Open edX platform to apply the changes:

.. code-block:: bash

     tutor local launch

3. Create and enable an Inline Tutor plugin to configure the n8n webhooks:

.. code-block:: python

     # Location plugins/n8n.py
     from tutor import hooks

     hooks.Filters.ENV_PATCHES.add_item(
         (
             "openedx-lms-common-settings",
     """
     N8N_REGISTRATION_WEBHOOK = "https://<your-n8n-domain>/webhook/<registration-path>"
     N8N_ENROLLMENT_WEBHOOK = "https://<your-n8n-domain>/webhook/<enrollment-path>"
     N8N_PERSISTENT_GRADE_COURSE_WEBHOOK = "https://<your-n8n-domain>/webhook/<grade-path>"
     """
         )
     )

.. code-block:: bash

     tutor plugins enable n8n

4. Configure n8n webhooks to receive JSON event data, follow the instructions available in the n8n documentation.
5. Trigger the events by registering a new user, enrolling in a course, or updating a grade in the Open edX platform.

To send event data to other services or APIs, simply configure more webhooks in the Django settings. The handlers are intentionally generic, ensuring they work seamlessly with different kinds of services. You can also add more event handlers to the `handlers.py`_ file to listen to additional events.

How to Extend this Repository
-----------------------------

This repository is a starting point for Open edX developers:

- You can add new event handlers by following the structure in `handlers.py`_.
- Custom logic can be implemented to fit your organization's data flow requirements using n8n, third-party APIs, or internal services.

For details on extending Open edX with Open edX Events, see also:

- `Open edX Events Documentation`_
- `Hooks Extension Framework`_

The openedx-events-2-n8n repository is here to make integrations simple and sustainable, giving developers the tools to create effective Open edX workflows with external services like n8n.

More Help
=========

If you're having trouble, we have discussion forums at
https://discuss.openedx.org where you can connect with others in the
community.

Our real-time conversations are on Slack. You can request a `Slack
invitation`_, then join our `community Slack workspace`_.

For anything non-trivial, the best path is to open an issue in this
repository with as many details about the issue you are facing as you
can provide.

https://github.com/Abstract-Tech/openedx-events-2-n8n/issues

For more information about these options, see the `Getting Help <https://openedx.org/getting-help>`__ page.

.. _Slack invitation: https://openedx.org/slack
.. _community Slack workspace: https://openedx.slack.com/

License
*******

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see `LICENSE.txt`_ for details.

Contributing
************

Contributions are very welcome.
Please read `How To Contribute <https://openedx.org/r/how-to-contribute>`_ for details.

This project is currently accepting all types of contributions, bug fixes,
security fixes, maintenance work, or new features.  However, please make sure
to discuss your new feature idea with the maintainers before beginning development
to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing
your idea.

The Open edX Code of Conduct
****************************

All community members are expected to follow the `Open edX Code of Conduct`_.

.. _Open edX Code of Conduct: https://openedx.org/code-of-conduct/

People
******

This repository is currently being maintained by the Abstract Technology team. See the `CODEOWNERS`_ file for details.

Reporting Security Issues
*************************

Please do not report security issues in public. Contact the Abstract Technology maintainers privately before publishing details.


.. _Hooks Extension Framework: https://open-edx-proposals.readthedocs.io/en/latest/oep-0050-hooks-extension-framework.html
.. _Open edX Events Documentation: https://docs.openedx.org/projects/openedx-events/en/latest/
.. _STUDENT_REGISTRATION_COMPLETED: https://docs.openedx.org/projects/openedx-events/en/latest/reference/events.html#openedxevent-org.openedx.learning.student.registration.completed.v1
.. _COURSE_ENROLLMENT_CREATED: https://docs.openedx.org/projects/openedx-events/en/latest/reference/events.html#openedxevent-org.openedx.learning.course.enrollment.created.v1
.. _PERSISTENT_GRADE_SUMMARY_CHANGED: https://docs.openedx.org/projects/openedx-events/en/latest/reference/events.html#openedxevent-org.openedx.learning.course.persistent_grade_summary.changed.v1
.. _handlers.py: https://github.com/Abstract-Tech/openedx-events-2-n8n/blob/main/openedx_events_2_n8n/handlers.py
.. _receiver: https://docs.djangoproject.com/en/4.2/topics/signals/#connecting-receiver-functions
.. _n8n webhook: https://n8n.com/
.. _Real-Life Use Cases for Open edX Events: https://docs.openedx.org/projects/openedx-events/en/latest/reference/real-life-use-cases.html
.. _Tutor plugin: https://docs.tutor.edly.io/plugins/intro.html#plugins
.. _Tutor documentation: https://docs.tutor.edly.io/
.. _CODEOWNERS: https://github.com/Abstract-Tech/openedx-events-2-n8n/blob/main/.github/CODEOWNERS
.. _LICENSE.txt: https://github.com/Abstract-Tech/openedx-events-2-n8n/blob/main/LICENSE.txt

.. |ci-badge| image:: https://github.com/Abstract-Tech/openedx-events-2-n8n/workflows/Python%20CI/badge.svg?branch=main
    :target: https://github.com/Abstract-Tech/openedx-events-2-n8n/actions
    :alt: CI

.. |license-badge| image:: https://img.shields.io/github/license/Abstract-Tech/openedx-events-2-n8n.svg
    :target: https://github.com/Abstract-Tech/openedx-events-2-n8n/blob/main/LICENSE.txt
    :alt: License
