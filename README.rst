================
Insight-Reloaded
================

Introduction
============

We are working to find the best solution for our previewer media server.

The case is simple, we have PDF and we want to preview them (small,
medium, large, header).

We first started with Insight_ which allows people to ask for sync
and async previews generations from an url with caching.

The system is able to register engines so that we can manipulate
documents on the flow.

The idea of Insight-Reloaded is to remove the sync mode and delegate
it to Nginx with disk or S3 storage.

If the document preview is not ready, we want a 404 error.

We will get the document preview url with a callback.

Service architecture
====================

.. image:: https://raw.github.com/novagile/insight-reloaded/master/docs/_static/InsightReloaded.png
.. _Insight: https://github.com/novagile/insight

Server provisioning
===================

You can find insight-reloaded chef cookbooks here : https://github.com/novagile/insight-installer
This will helps you install all requirements to run your insight-reloaded server.