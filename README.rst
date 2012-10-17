================
Insight-Reloaded
================

We are working to find the best solution for our previewer media server.

The case is simple, we have PDF and we want to preview them (small,
medium, large, header).

We first started with Insight_ which allows people to ask for sync
and async previews generations from an url with caching.

The system is able to register engines so that we can manipulate
documents on the flow.

The idea of Insight-Reloaded is to remove the async mode and delegate
it to Nginx.

If the document preview is not ready, we want a 404 error.

We will get the document preview url with a callback.

.. image:: insight-reloaded/docs/_static/InsightReloaded.png
.. _Insight: https://github.com/novagile/insight
