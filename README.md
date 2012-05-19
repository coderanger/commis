## WHAT

Commis is a [Django](http://djangoproject.com) implementation of [Chef
Server](http://wiki.opscode.com/display/chef/Chef+Server). It's currently
compatible with Django 1.2 through 1.4, and thus has the same dependencies as
those releases:

* Python 2.5 or newer
* A relational database engine (this includes the ships-with-Python SQLite)

On top of that, Commis requires a handful of other pure-Python libraries, such
as PyChef, Celery and PyParsing.


## WHY

There are a number of reasons you may want to deploy Commis instead of the
standard Chef Server implementation or using Opscode's hosted service:

### Simpler deployment

**Chef Server requires many components & runtimes in addition to Ruby**:
RabbitMQ (and thus Erlang), CouchDB (also Erlang), Solr (Java), and `gecode`.
Installation quickly gets complicated on non-Ubuntu platforms such as CentOS or
Fedora (have fun finding up to date `gecode` RPMs or waiting an hour for it to
compile!).  Managing and supporting the different components is also a large
hurdle for users who just want to get started, regardless of platform.

Conversely, in its most basic form, **Commis relies purely upon Python
libraries** -- the embedded SQLite for databasing, Whoosh for text indexing,
and Celery for queuing (which can function without an actual queue when not
needed.)

Furthermore, **you can easily replace these components when necessary, and with
whatever backends you want**.  SQLite crumbles with more than a few concurrent
users? Use Postgres or MySQL (or Oracle or ...). Need non-eager background
jobs? Use any [Celery](http://celeryproject.org/)-supported backend (like
Redis), you're not limited to RabbitMQ. Ditto for text indexing -- anything
[Haystack](http://haystacksearch.org/) supports is fair game.

### Improved hackability

As a third party solution, Commis is free to innovate and add experimental
features that aren't suitable for the official Chef Server project. This
includes things like major UI changes for the web interface and flexible policy
backends that are designed be be altered to suit your needs.

For example, not everybody is able or willing to treat their Chef Server as the
single source of truth -- imagine being able to plug-in or sync your
pre-existing LDAP server or Clusto database such that your Chef recipes see the
data as regular attributes, or even as dynamically managed node or client
entries. And this is just one example.

### Python interoperability

Mostly a sub-case of the above -- Commis, being Python, is a great fit for
shops with pre-existing Python systems or Python deployment experience.
Learning Ruby to write Chef manifests is one thing; becoming comfortable
deploying a complex Ruby web-app is another entirely. With Commis, you might
not have to.


## HOW

Here's how to get started hacking on or evaluating Commis. It assumes you want
to run off the abovementioned pure-Python default stack; to move away from
those defaults, you'll just need to install the additional components you want
and modify `commis/settings.py` appropriately.

On the system acting as Chef Server:

* Clone, download tarball, etc.
* `pip install -r requirements.txt`
* `python commis/manage.py syncdb` to impress the SQL schema onto the default
  SQLite database.
    * By default, this database lives in `commis/commis.db`. As always, you can
    change this in `commis/settings.py`.
    * It will prompt you for a new admin user -- make sure you keep track of
    this as it's how you will login to the Web UI and manage everything.
* `python commis/manage.py runserver 0.0.0.0:8000`
    * Obviously you may alter the port number to taste.
    * Commis currently runs both the Web UI and the REST API on the same Web
    worker/port. API requests go to `/api/*` while everything else is assumed
    to be part of the regular Web app. By contrast, Chef Server runs the API
    off port 4000 and the Web UI off 4040, by default.

### TK

* Setting up an admin user with `manage.py commis_client <name>` -- or does
  `syncdb` do that for you now? can't remember.
* Setting up the validator client/certificate (ditto)
* Is `manage.py migrate` required? ISTR running it at one point.
* Configure a knife install on some workstation
* Upload your cookbooks, if any
    * Doesn't require a cookbooks repo, AFAICT -- I just manually pointed it at
    cookbooks in a shared repo.
* Test by running `chef-client` on a new box:
    * Set `/etc/chef/client.rb` to use a URI of `http://commis_server:8000/api`
    - the `/api` is an important distinction from Chef Server!
